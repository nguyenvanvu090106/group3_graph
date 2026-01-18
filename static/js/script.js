// ==========================================
// 1. CONFIGURATION & CONSTANTS
// ==========================================
const VERTEX_RADIUS = 20
const COLORS = {
  DEFAULT: '#3498db',
  BORDER: '#2980b9',
  TEXT: '#ffffff',

  SELECTED: '#e74c3c',
  EDGE: '#2c3e50',

  SOURCE: '#e67e22', // Cam (Nguồn)
  TARGET: '#9b59b6', // Tím (Đích/Sink)

  FLOW_EDGE: '#f39c12',
  FLOW_TEXT: '#d35400',
  FLOW_BG: '#ffffff',
  EMPTY_EDGE: '#95a5a6',

  ANIM_EDGE_DONE: '#e67e22',
  ANIM_EDGE_GROWING: '#f39c12',

  NODE_ACTIVE_BG: '#e67e22',
  NODE_ACTIVE_BORDER: '#d35400',

  BIPARTITE_A: '#e74c3c',
  BIPARTITE_B: '#2ecc71',

  BADGE_BG: '#ffffff',
  BADGE_TEXT: '#d35400',
  BADGE_BORDER: '#d35400',

  ANIM_AGENT: '#c0392b',
}

// ==========================================
// 2. STATE MANAGEMENT
// ==========================================
let nodes = []
let edges = []
let nextId = 0

// [UNDO/REDO] Lịch sử trạng thái
let historyStack = []
let redoStack = []

let isDirected = false
let globalDirectedState = false
let namingMode = '0, 1, 2...'

let currentMode = 'MOVE'
let selectedNode = null
let dragNode = null

let currentAlgo = null
let algoSourceNode = null
let algoTargetNode = null
let algoStep = 0
let algoResult = null

let animState = {
  active: false,
  type: null,
  data: [],
  segmentIndex: 0,
  progress: 0,
  speed: 0.015,
  reqId: null,
}

let tempSourceNode = null
let tempTargetNode = null
let itemToDelete = null

// ==========================================
// 3. CANVAS SETUP
// ==========================================
const canvas = document.getElementById('graphCanvas')
const ctx = canvas.getContext('2d')

function resizeCanvas() {
  if (canvas && canvas.parentElement) {
    canvas.width = canvas.parentElement.clientWidth
    canvas.height = canvas.parentElement.clientHeight
    if (!animState.active) draw()
  }
}
window.addEventListener('resize', resizeCanvas)
setTimeout(resizeCanvas, 100)

// ==========================================
// 4. HELPER FUNCTIONS
// ==========================================
function getDistance(x1, y1, x2, y2) {
  return Math.sqrt(Math.pow(x2 - x1, 2) + Math.pow(y2 - y1, 2))
}
function getNodeAt(x, y) {
  for (let i = nodes.length - 1; i >= 0; i--) {
    if (getDistance(x, y, nodes[i].x, nodes[i].y) <= VERTEX_RADIUS) return nodes[i]
  }
  return null
}

function getEdgeAt(mx, my) {
  const threshold = 8
  for (let i = 0; i < edges.length; i++) {
    let e = edges[i]
    let u = nodes.find((n) => n.id === e.source)
    let v = nodes.find((n) => n.id === e.target)
    if (!u || !v) continue

    if (isBidirectional(e)) {
      const { cpX, cpY } = calculateControlPoint(u, v)
      const midCurveX = (u.x + 2 * cpX + v.x) / 4
      const midCurveY = (u.y + 2 * cpY + v.y) / 4
      if (getDistance(mx, my, midCurveX, midCurveY) < 20) return e
    } else {
      let distSq = distToSegmentSquared({ x: mx, y: my }, u, v)
      if (distSq <= threshold * threshold) return e
    }
  }
  return null
}

function distToSegmentSquared(p, v, w) {
  let l2 = Math.pow(v.x - w.x, 2) + Math.pow(v.y - w.y, 2)
  if (l2 === 0) return Math.pow(p.x - v.x, 2) + Math.pow(p.y - v.y, 2)
  let t = ((p.x - v.x) * (w.x - v.x) + (p.y - v.y) * (w.y - v.y)) / l2
  t = Math.max(0, Math.min(1, t))
  return Math.pow(p.x - v.x - t * (w.x - v.x), 2) + Math.pow(p.y - v.y - t * (w.y - v.y), 2)
}
function updateNamingMode() {
  namingMode = document.getElementById('enum-select').value
}
function generateLabel(id) {
  if (namingMode === '1, 2, 3...') return (id + 1).toString()
  else if (namingMode === 'A, B, C...') {
    if (id < 26) return String.fromCharCode(65 + id)
    return String.fromCharCode(65 + (id % 26)) + Math.floor(id / 26)
  }
  return id.toString()
}

// ==========================================
// 5. UNDO / REDO & SAVE SYSTEM
// ==========================================

function saveState() {
  if (historyStack.length > 20) historyStack.shift()
  const currentState = JSON.stringify({
    nodes: nodes,
    edges: edges,
    nextId: nextId,
    directed: globalDirectedState,
  })
  historyStack.push(currentState)
  redoStack = []
}

function undo() {
  if (historyStack.length === 0) {
    setNotification('Nothing to Undo.', 'default')
    return
  }
  const currentState = JSON.stringify({
    nodes: nodes,
    edges: edges,
    nextId: nextId,
    directed: globalDirectedState,
  })
  redoStack.push(currentState)

  const prevState = JSON.parse(historyStack.pop())
  nodes = prevState.nodes
  edges = prevState.edges
  nextId = prevState.nextId
  globalDirectedState = prevState.directed

  document.getElementById('chk-directed').checked = globalDirectedState

  // Reset algo khi undo
  algoResult = null
  algoSourceNode = null
  algoTargetNode = null

  draw()
  setNotification('Undone.', 'default')
}

function redo() {
  if (redoStack.length === 0) {
    setNotification('Nothing to Redo.', 'default')
    return
  }
  const currentState = JSON.stringify({
    nodes: nodes,
    edges: edges,
    nextId: nextId,
    directed: globalDirectedState,
  })
  historyStack.push(currentState)

  const nextState = JSON.parse(redoStack.pop())
  nodes = nextState.nodes
  edges = nextState.edges
  nextId = nextState.nextId
  globalDirectedState = nextState.directed

  document.getElementById('chk-directed').checked = globalDirectedState

  algoResult = null
  algoSourceNode = null
  algoTargetNode = null

  draw()
  setNotification('Redone.', 'default')
}

window.addEventListener('keydown', (e) => {
  if ((e.ctrlKey || e.metaKey) && e.key === 'z') {
    e.preventDefault()
    undo()
  }
  if ((e.ctrlKey || e.metaKey) && (e.key === 'y' || (e.shiftKey && e.key === 'Z'))) {
    e.preventDefault()
    redo()
  }
})

function saveGraph() {
  const link = document.createElement('a')
  link.download = 'my_graph_snapshot.png'
  link.href = canvas.toDataURL('image/png')
  link.click()
  setNotification('Image saved to computer!', 'success')
}

// ==========================================
// 6. MODAL & ACTIONS
// ==========================================
function closeModal() {
  const ids = [
    'modal-overlay',
    'weight-modal',
    'clear-modal',
    'delete-item-modal',
    'result-text-modal',
  ]
  ids.forEach((id) => {
    const el = document.getElementById(id)
    if (el) el.style.display = 'none'
  })
  tempSourceNode = null
  tempTargetNode = null
  selectedNode = null
  draw()
}
function askToClear() {
  document.getElementById('modal-overlay').style.display = 'flex'
  document.getElementById('clear-modal').style.display = 'block'
}
function performClear() {
  saveState()
  stopAnimation()
  nodes = []
  edges = []
  nextId = 0

  // Reset thuật toán
  algoResult = null
  algoSourceNode = null
  algoTargetNode = null

  closeModal()
  setNotification('Graph cleared.', 'default')
  draw()
}
function confirmAddEdge() {
  const weightInput = document.getElementById('modal-weight-input')
  const w = parseInt(weightInput.value) || 1
  if (tempSourceNode && tempTargetNode) {
    saveState()
    addEdge(tempSourceNode, tempTargetNode, w, true)
    selectedNode = null
    setNotification('Edge created. Select new Source.', 'success')
  }
  closeModal()
  tempSourceNode = null
  tempTargetNode = null
  draw()
}

function deleteDirectly(item, type) {
  saveState()
  stopAnimation()

  // Reset thuật toán khi xóa để tránh lỗi
  algoResult = null
  algoSourceNode = null
  algoTargetNode = null

  if (type === 'node') {
    const nodeId = item.id
    nodes = nodes.filter((n) => n.id !== nodeId)
    edges = edges.filter((e) => e.source !== nodeId && e.target !== nodeId)
  } else if (type === 'edge') {
    edges = edges.filter((e) => e !== item)
  }
  draw()
}

function askToDeleteItem(item, type) {}
function confirmDeleteItem() {}

const wInput = document.getElementById('modal-weight-input')
if (wInput) {
  wInput.addEventListener('keypress', function (e) {
    if (e.key === 'Enter') confirmAddEdge()
  })
}

function addEdge(u, v, w, showWeight) {
  edges = edges.filter((e) => {
    const isConnecting =
      (e.source === u.id && e.target === v.id) || (e.source === v.id && e.target === u.id)
    if (isConnecting) {
      if (!globalDirectedState) return false
      if (!e.isDirected) return false
      if (e.source === u.id && e.target === v.id) return false
      if (e.source === v.id && e.target === u.id) return true
    }
    return true
  })

  edges.push({
    source: u.id,
    target: v.id,
    weight: w,
    isDirected: globalDirectedState,
    showWeight: showWeight,
  })

  algoResult = null
  stopAnimation()
  draw()
}

// ==========================================
// 7. ALGORITHM LOGIC (CONTROLLER)
// ==========================================
function prepareAlgorithm() {
  const select = document.getElementById('algo-select')
  currentAlgo = select.value
  if (!currentAlgo) return
  stopAnimation()
  algoSourceNode = null
  algoTargetNode = null
  algoResult = null
  document.querySelectorAll('.btn-mode').forEach((b) => b.classList.remove('active'))
  currentMode = 'ALGO_INPUT'
  updateSettingsPanel('ALGO_INPUT')
  const algoName = currentAlgo.toUpperCase()
  if (['bfs', 'dfs', 'prim', 'fleury', 'hierholzer'].includes(currentAlgo)) {
    algoStep = 1
    setNotification(`Select  <pre> START VERTEX </pre> for ${algoName}.`, 'default')
  } else if (['dijkstra', 'max_flow'].includes(currentAlgo)) {
    algoStep = 1
    setNotification(`Select  <pre> SOURCE VERTEX </pre> for ${algoName}.`, 'default')
  } else if (['kruskal', 'bipartite'].includes(currentAlgo)) {
    setNotification('Running Algorithm...', 'default')
    runAlgorithmAPI()
  }
  draw()
}
function cancelAlgorithm() {
  stopAnimation()
  const sel = document.getElementById('algo-select')
  if (sel) sel.value = ''
  setMode('MOVE') // Hàm setMode sẽ lo việc reset
}
function handleNodeClickForAlgo(node) {
  if (algoResult || algoStep === 0) {
    stopAnimation()
    algoResult = null
    algoSourceNode = null
    algoTargetNode = null
    algoStep = 1
  }
  if (algoStep === 1) {
    algoSourceNode = node
    draw()
    if (['bfs', 'dfs', 'prim', 'fleury', 'hierholzer'].includes(currentAlgo)) {
      setNotification('Processing...', 'default')
      runAlgorithmAPI()
      algoStep = 0
    } else {
      algoStep = 2
      const targetName = currentAlgo === 'max_flow' ? ' SINK ' : ' TARGET '
      setNotification(` Start: <b> ${node.label} </b>. Click <b> ${targetName} </b>.`, 'default')
    }
  } else if (algoStep === 2) {
    if (node === algoSourceNode) {
      setNotification('Source & Target cannot be same!', 'error')
      return
    }
    algoTargetNode = node
    draw()
    setNotification('Processing...', 'default')
    runAlgorithmAPI()
    algoStep = 0
  }
}

// ==========================================
// 8. ANIMATION SYSTEM
// ==========================================
function startAnimation(type, data) {
  if (!data || data.length < 1) return
  animState.type = type
  animState.data = data
  animState.segmentIndex = 0
  animState.progress = 0
  animState.active = true
  if (animState.reqId) cancelAnimationFrame(animState.reqId)
  animateLoop()
}
function stopAnimation() {
  animState.active = false
  if (animState.reqId) cancelAnimationFrame(animState.reqId)
  animState.reqId = null
  draw()
}
function animateLoop() {
  if (!animState.active) return
  animState.progress += animState.speed
  if (animState.progress >= 1.0) {
    animState.progress = 0
    animState.segmentIndex++
    let max = animState.type === 'path' ? animState.data.length - 1 : animState.data.length
    if (animState.segmentIndex >= max) {
      animState.active = false
      draw()
      return
    }
  }
  draw()
  animState.reqId = requestAnimationFrame(animateLoop)
}

// ==========================================
// 9. RENDERER (VẼ VÀ HIỆU ỨNG)
// ==========================================
function draw() {
  try {
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    if (currentAlgo === 'max_flow' && algoResult && algoResult.flow_edges) {
      drawMaxFlowState()
      return
    }
    edges.forEach((edge) => {
      const u = nodes.find((n) => n.id === edge.source)
      const v = nodes.find((n) => n.id === edge.target)
      if (!u || !v) return
      drawEdge(u, v, edge, COLORS.EDGE, 2)
    })
    if (algoResult) drawAlgorithmAnimation()
    nodes.forEach((node) => {
      let color = node.color || COLORS.DEFAULT
      let borderColor = COLORS.BORDER
      let lineWidth = 1

      // Highlight Source/Target nếu đang trong mode Algorithm
      if (node === algoSourceNode) {
        color = COLORS.SOURCE
        lineWidth = 3
      }
      if (node === algoTargetNode) {
        color = COLORS.TARGET
        lineWidth = 3
      }
      if (selectedNode === node) {
        borderColor = COLORS.SELECTED
        lineWidth = 3
      }

      if (
        currentAlgo === 'bipartite' &&
        algoResult &&
        algoResult.is_bipartite &&
        algoResult.colors
      ) {
        if (algoResult.colors[node.id] === 0) color = COLORS.BIPARTITE_A
        else if (algoResult.colors[node.id] === 1) color = COLORS.BIPARTITE_B
      } else if (algoResult) {
        let shouldHighlight = false
        if (algoResult.path && animState.type === 'path') {
          if (algoResult.path.includes(node.id) && !animState.active) shouldHighlight = true
        }
        if (shouldHighlight) {
          color = COLORS.NODE_ACTIVE_BG
          borderColor = COLORS.NODE_ACTIVE_BORDER
          lineWidth = 3
        }
      }
      drawNodeCircle(node, color, borderColor, lineWidth, null)
    })
    if (algoResult && algoResult.path && ['bfs', 'dfs'].includes(currentAlgo))
      drawTraversalOrder(algoResult.path)
    if (animState.active && animState.type === 'path') drawMovingAgent()
  } catch (err) {
    console.error('Draw error:', err)
  }
}

function drawMaxFlowState() {
  edges.forEach((edge) => {
    const u = nodes.find((n) => n.id === edge.source)
    const v = nodes.find((n) => n.id === edge.target)
    if (!u || !v) return
    const flowData = algoResult.flow_edges.find((f) => f.u === u.id && f.v === v.id)
    let label = `0 / ${edge.weight}`
    let color = COLORS.EMPTY_EDGE
    let width = 2
    if (flowData) {
      label = `${flowData.flow} / ${edge.weight}`
      if (flowData.flow > 0) {
        color = COLORS.FLOW_EDGE
        width = 4
      }
    }
    drawEdge(u, v, edge, color, width, label)
  })
  nodes.forEach((node) => {
    let color = COLORS.DEFAULT
    let borderColor = COLORS.BORDER
    let labelAbove = null
    if (algoSourceNode && node.id === algoSourceNode.id) {
      color = COLORS.SOURCE
      borderColor = '#d35400'
      labelAbove = 'Source'
    } else if (algoTargetNode && node.id === algoTargetNode.id) {
      color = COLORS.TARGET
      borderColor = '#8e44ad'
      labelAbove = 'Sink'
    }
    drawNodeCircle(node, color, borderColor, 2, labelAbove)
  })
}

function drawNodeCircle(node, color, borderColor, lineWidth, labelAbove = null) {
  ctx.beginPath()
  ctx.arc(node.x, node.y, VERTEX_RADIUS, 0, 2 * Math.PI)
  ctx.fillStyle = color
  ctx.fill()
  ctx.strokeStyle = borderColor
  ctx.lineWidth = lineWidth
  ctx.stroke()
  ctx.fillStyle = COLORS.TEXT
  ctx.font = 'bold 14px Arial'
  ctx.textAlign = 'center'
  ctx.textBaseline = 'middle'
  ctx.fillText(node.label, node.x, node.y)
  if (labelAbove) {
    ctx.fillStyle = color
    ctx.font = 'bold 14px Arial'
    ctx.textAlign = 'center'
    ctx.textBaseline = 'bottom'
    ctx.fillText(labelAbove, node.x, node.y - VERTEX_RADIUS - 8)
  }
}

function drawAlgorithmAnimation() {
  if (animState.type === 'path' && animState.data) {
    const path = animState.data
    for (let i = 0; i < path.length - 1; i++) {
      let u = nodes.find((n) => n.id === path[i])
      let v = nodes.find((n) => n.id === path[i + 1])
      let edge = findEdgeForDrawing(u.id, v.id)
      if (u && v && edge) {
        if (!animState.active || i < animState.segmentIndex)
          drawEdge(u, v, edge, COLORS.ANIM_EDGE_DONE, 6)
        else if (animState.active && i === animState.segmentIndex)
          drawGrowingEdge(u, v, edge, COLORS.ANIM_EDGE_GROWING, 6, animState.progress)
      }
    }
  } else if (animState.type === 'edges' && animState.data) {
    const visited = animState.data
    const limit = animState.active ? animState.segmentIndex + 1 : visited.length
    let traversedSet = new Set()
    if (algoSourceNode) traversedSet.add(algoSourceNode.id)
    for (let i = 0; i < limit; i++) {
      if (i >= visited.length) break
      const edgeObj = visited[i]
      let u = nodes.find((n) => n.id === edgeObj.u)
      let v = nodes.find((n) => n.id === edgeObj.v)
      let edge = findEdgeForDrawing(u.id, v.id)
      if (u && v && edge) {
        let startNode = u
        let endNode = v
        if (traversedSet.has(v.id) && !traversedSet.has(u.id)) {
          startNode = v
          endNode = u
        }
        traversedSet.add(u.id)
        traversedSet.add(v.id)
        if (animState.active && i === animState.segmentIndex)
          drawGrowingEdge(startNode, endNode, edge, COLORS.ANIM_EDGE_GROWING, 6, animState.progress)
        else drawEdge(startNode, endNode, edge, COLORS.ANIM_EDGE_DONE, 6)
      }
    }
  } else if (algoResult.mst_edges) {
    algoResult.mst_edges.forEach((edgeObj) => {
      let u = nodes.find((n) => n.id === edgeObj.u)
      let v = nodes.find((n) => n.id === edgeObj.v)
      let edge = findEdgeForDrawing(u.id, v.id)
      if (u && v && edge) drawEdge(u, v, edge, COLORS.ANIM_EDGE_DONE, 5)
    })
  }
}

function findEdgeForDrawing(uId, vId) {
  return edges.find(
    (e) => (e.source === uId && e.target === vId) || (e.source === vId && e.target === uId)
  )
}
function isBidirectional(edge) {
  if (!edge.isDirected) return false
  return edges.some((e) => e !== edge && e.source === edge.target && e.target === edge.source)
}
function calculateControlPoint(u, v) {
  const midX = (u.x + v.x) / 2
  const midY = (u.y + v.y) / 2
  const dx = v.x - u.x
  const dy = v.y - u.y
  const dist = Math.sqrt(dx * dx + dy * dy)
  let nx = -dy / dist
  let ny = dx / dist
  const curveAmount = 35
  return { cpX: midX + nx * curveAmount, cpY: midY + ny * curveAmount }
}

function drawEdge(u, v, edge, color, width, customLabel = null) {
  const isCurved = isBidirectional(edge)
  ctx.beginPath()
  if (isCurved) {
    const { cpX, cpY } = calculateControlPoint(u, v)
    ctx.moveTo(u.x, u.y)
    ctx.quadraticCurveTo(cpX, cpY, v.x, v.y)
    ctx.strokeStyle = color
    ctx.lineWidth = width
    ctx.stroke()
    if (edge.isDirected) {
      drawArrowEndCurve(u, v, cpX, cpY, color, width)
    }
    if (customLabel) drawWeightOnCurve(cpX, cpY, customLabel, true)
    else if (edge.showWeight) drawWeightOnCurve(cpX, cpY, edge.weight, false)
  } else {
    const angle = Math.atan2(v.y - u.y, v.x - u.x)
    const startX = u.x + VERTEX_RADIUS * Math.cos(angle)
    const startY = u.y + VERTEX_RADIUS * Math.sin(angle)
    const endX = v.x - VERTEX_RADIUS * Math.cos(angle)
    const endY = v.y - VERTEX_RADIUS * Math.sin(angle)
    ctx.moveTo(startX, startY)
    ctx.lineTo(endX, endY)
    ctx.strokeStyle = color
    ctx.lineWidth = width
    ctx.stroke()
    if (edge.isDirected) {
      drawArrowAt(endX, endY, angle, color, width)
    }
    const midX = (u.x + v.x) / 2
    const midY = (u.y + v.y) / 2
    if (customLabel) drawWeightBox(midX, midY, customLabel, true)
    else if (edge.showWeight) drawWeightBox(midX, midY, edge.weight, false)
  }
}

function drawArrowEndCurve(u, v, cpX, cpY, color, width) {
  const angle = Math.atan2(v.y - cpY, v.x - cpX)
  const arrowX = v.x - VERTEX_RADIUS * Math.cos(angle)
  const arrowY = v.y - VERTEX_RADIUS * Math.sin(angle)
  drawArrowAt(arrowX, arrowY, angle, color, width)
}
function drawArrowAt(x, y, angle, color, width) {
  const headLen = 12 + width * 0.5
  ctx.beginPath()
  ctx.moveTo(x, y)
  ctx.lineTo(
    x - headLen * Math.cos(angle - Math.PI / 6),
    y - headLen * Math.sin(angle - Math.PI / 6)
  )
  ctx.lineTo(
    x - headLen * Math.cos(angle + Math.PI / 6),
    y - headLen * Math.sin(angle + Math.PI / 6)
  )
  ctx.lineTo(x, y)
  ctx.fillStyle = color
  ctx.fill()
}
function drawGrowingEdge(u, v, edge, color, width, progress) {
  const isCurved = isBidirectional(edge)
  ctx.beginPath()
  if (isCurved) {
    const { cpX, cpY } = calculateControlPoint(u, v)
    ctx.moveTo(u.x, u.y)
    for (let t = 0; t <= progress; t += 0.02) {
      let xt = (1 - t) * (1 - t) * u.x + 2 * (1 - t) * t * cpX + t * t * v.x
      let yt = (1 - t) * (1 - t) * u.y + 2 * (1 - t) * t * cpY + t * t * v.y
      ctx.lineTo(xt, yt)
    }
  } else {
    const destX = u.x + (v.x - u.x) * progress
    const destY = u.y + (v.y - u.y) * progress
    ctx.moveTo(u.x, u.y)
    ctx.lineTo(destX, destY)
  }
  ctx.strokeStyle = color
  ctx.lineWidth = width
  ctx.lineCap = 'round'
  ctx.stroke()
  ctx.lineCap = 'butt'
}
function drawWeightOnCurve(x, y, text, isFlowLabel = false) {
  drawWeightBox(x, y, text, isFlowLabel)
}
function drawWeightBox(x, y, text, isFlowLabel = false) {
  ctx.font = 'bold 12px Arial'
  const textMetrics = ctx.measureText(text)
  const w = textMetrics.width + 10
  const h = 20
  ctx.fillStyle = isFlowLabel ? COLORS.FLOW_BG : 'white'
  ctx.strokeStyle = isFlowLabel ? COLORS.FLOW_TEXT : '#ccc'
  ctx.lineWidth = isFlowLabel ? 2 : 1
  ctx.beginPath()
  ctx.rect(x - w / 2, y - h / 2, w, h)
  ctx.fill()
  ctx.stroke()
  ctx.fillStyle = isFlowLabel ? COLORS.FLOW_TEXT : 'red'
  ctx.textAlign = 'center'
  ctx.textBaseline = 'middle'
  ctx.fillText(text, x, y)
}
function drawMovingAgent() {
  const pathIds = animState.data
  const idx = animState.segmentIndex
  if (idx >= pathIds.length - 1) return
  const u = nodes.find((n) => n.id === pathIds[idx])
  const v = nodes.find((n) => n.id === pathIds[idx + 1])
  if (u && v) {
    const currentX = u.x + (v.x - u.x) * animState.progress
    const currentY = u.y + (v.y - u.y) * animState.progress
    const size = 16
    ctx.fillStyle = COLORS.ANIM_AGENT
    ctx.shadowBlur = 10
    ctx.shadowColor = COLORS.ANIM_AGENT
    ctx.save()
    ctx.translate(currentX, currentY)
    ctx.rotate(animState.progress * Math.PI * 2)
    ctx.fillRect(-size / 2, -size / 2, size, size)
    ctx.restore()
    ctx.shadowBlur = 0
  }
}
function drawTraversalOrder(pathIds) {
  const limit = animState.active ? animState.segmentIndex + 1 : pathIds.length
  pathIds.forEach((nodeId, index) => {
    if (index >= limit) return
    let node = nodes.find((n) => n.id === nodeId)
    if (node) {
      const badgeX = node.x + VERTEX_RADIUS * 0.8
      const badgeY = node.y - VERTEX_RADIUS * 0.8
      ctx.beginPath()
      ctx.arc(badgeX, badgeY, 10, 0, 2 * Math.PI)
      ctx.fillStyle = COLORS.BADGE_BG
      ctx.fill()
      ctx.strokeStyle = COLORS.BADGE_BORDER
      ctx.lineWidth = 2
      ctx.stroke()
      ctx.fillStyle = COLORS.BADGE_TEXT
      ctx.font = 'bold 11px Arial'
      ctx.textAlign = 'center'
      ctx.textBaseline = 'middle'
      ctx.fillText(index + 1, badgeX, badgeY)
    }
  })
}

// [MODIFIED] CONTROLLER: XÓA NGAY LẬP TỨC + UNDO/REDO
canvas.addEventListener('mousedown', (e) => {
  const rect = canvas.getBoundingClientRect()
  const x = e.clientX - rect.left
  const y = e.clientY - rect.top
  const clickedNode = getNodeAt(x, y)
  if (currentMode === 'ALGO_INPUT') {
    if (clickedNode) handleNodeClickForAlgo(clickedNode)
    return
  }
  stopAnimation()
  if (currentMode === 'ADD_VERTEX') {
    if (!clickedNode) {
      saveState() // [UNDO]
      const label = generateLabel(nextId)
      nodes.push({ id: nextId, x: x, y: y, label: label })
      nextId++
      draw()
    }
  } else if (currentMode === 'MOVE') {
    if (clickedNode) dragNode = clickedNode
  } else if (currentMode === 'ADD_EDGE') {
    if (clickedNode) {
      if (!selectedNode) {
        selectedNode = clickedNode
        setNotification(`Source: <b> ${selectedNode.label} </b>. Select Target.`, 'default')
        draw()
      } else {
        if (selectedNode !== clickedNode) {
          const isWeighted = document.getElementById('chk-weighted').checked
          if (isWeighted) {
            tempSourceNode = selectedNode
            tempTargetNode = clickedNode
            document.getElementById('modal-weight-input').value = '1'
            document.getElementById('modal-overlay').style.display = 'flex'
            document.getElementById('weight-modal').style.display = 'block'
            document.getElementById('modal-weight-input').focus()
            document.getElementById('modal-weight-input').select()
          } else {
            saveState() // [UNDO]
            addEdge(selectedNode, clickedNode, 1, false)
            selectedNode = null
            setNotification('Edge created. Select new Source.', 'success')
            draw()
          }
        } else {
          selectedNode = null
          setNotification('Select Source Vertex.', 'default')
          draw()
        }
      }
    } else {
      selectedNode = null
      draw()
    }
  } else if (currentMode === 'REMOVE') {
    if (clickedNode) {
      deleteDirectly(clickedNode, 'node')
    } else {
      const clickedEdge = getEdgeAt(x, y)
      if (clickedEdge) {
        deleteDirectly(clickedEdge, 'edge')
      }
    }
  }
})
canvas.addEventListener('mousemove', (e) => {
  if (currentMode === 'MOVE' && dragNode) {
    const rect = canvas.getBoundingClientRect()
    dragNode.x = e.clientX - rect.left
    dragNode.y = e.clientY - rect.top
    draw()
  }
})
canvas.addEventListener('mouseup', () => {
  dragNode = null
})

// [FIX] Cập nhật setMode để xóa màu Source/Target
function setMode(mode) {
  currentMode = mode
  selectedNode = null
  if (mode !== 'ALGO_INPUT') {
    const sel = document.getElementById('algo-select')
    if (sel) sel.value = ''
    algoResult = null
    algoSourceNode = null
    algoTargetNode = null
    algoStep = 0
    stopAnimation()
    resetColors()
  }
  document.querySelectorAll('.btn-mode').forEach((b) => b.classList.remove('active'))
  const idMap = {
    MOVE: 'btn-move',
    ADD_VERTEX: 'btn-add-vertex',
    ADD_EDGE: 'btn-add-edge',
    REMOVE: 'btn-remove',
  }
  if (idMap[mode]) document.getElementById(idMap[mode]).classList.add('active')
  updateSettingsPanel(mode)
}

function updateSettingsPanel(mode) {
  const ids = [
    'vertex-settings',
    'edge-settings',
    'remove-settings',
    'algo-settings',
    'no-settings',
  ]
  ids.forEach((id) => (document.getElementById(id).style.display = 'none'))
  let msg = 'Welcome!'
  let type = 'default'
  if (mode === 'ADD_VERTEX') {
    document.getElementById('vertex-settings').style.display = 'block'
    msg = 'Click to add vertex.'
  } else if (mode === 'ADD_EDGE') {
    document.getElementById('edge-settings').style.display = 'block'
    msg = 'Select <b>Source Vertex</b>.'
  } else if (mode === 'REMOVE') {
    document.getElementById('remove-settings').style.display = 'block'
    msg = 'Click Node/Edge to delete instantly.'
  } else if (mode === 'ALGO_INPUT') {
    document.getElementById('algo-settings').style.display = 'block'
  } else {
    document.getElementById('no-settings').style.display = 'block'
  }
  if (mode !== 'ALGO_INPUT') setNotification(msg, type)
}
function setNotification(msg, type) {
  const el = document.getElementById('notification')
  el.innerHTML = msg
  el.classList.remove('error', 'success', 'max_flow')
  if (type === 'error') el.classList.add('error')
  if (type === 'success') el.classList.add('success')
  if (type === 'max_flow') el.classList.add('max_flow')
}
function toggleDirected() {
  globalDirectedState = document.getElementById('chk-directed').checked
}
function resetColors() {
  nodes.forEach((n) => (n.color = null))
  edges.forEach((e) => {
    e.color = null
    e.width = 2
  })
  draw()
}
async function runAlgorithmAPI() {
  if (!currentAlgo) return
  const payload = {
    graph: { nodes: nodes, edges: edges, directed: globalDirectedState },
    type: currentAlgo,
  }
  if (algoSourceNode) {
    payload.startId = algoSourceNode.id
    payload.sourceId = algoSourceNode.id
  }
  if (algoTargetNode) {
    payload.endId = algoTargetNode.id
    payload.sinkId = algoTargetNode.id
  }
  let endpoint = `/api/${currentAlgo}`
  if (['prim', 'kruskal'].includes(currentAlgo)) endpoint = '/api/mst'
  if (['fleury', 'hierholzer'].includes(currentAlgo)) endpoint = '/api/euler'
  try {
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
    const result = await response.json()
    if (result.status === 'error') {
      setNotification(`⚠️ ${result.message}`, 'error')
      algoResult = null
    } else {
      algoResult = result
      displayResultText(result)
      if (['bfs', 'dfs'].includes(currentAlgo)) {
        if (result.visited_edges && result.visited_edges.length > 0)
          startAnimation('edges', result.visited_edges)
      } else if (result.path && result.path.length > 1) {
        startAnimation('path', result.path)
      }
    }
    draw()
  } catch (e) {
    console.error(e)
    setNotification('⚠️ Server Error.', 'error')
  }
}
function displayResultText(res) {
  let msg = ''
  const algoNameMap = {
    bfs: 'BFS',
    dfs: 'DFS',
    dijkstra: 'Dijkstra',
    prim: 'Prim MST',
    kruskal: 'Kruskal MST',
    fleury: 'Fleury',
    hierholzer: 'Hierholzer',
    max_flow: 'Max Flow',
    bipartite: 'Bipartite',
  }
  const prettyAlgo = algoNameMap[currentAlgo] || currentAlgo
  if (res.path && ['dijkstra'].includes(currentAlgo)) {
    const labels = res.path.map((id) => nodes.find((n) => n.id === id).label)
    msg = `${prettyAlgo}: <b>${labels.join(' → ')}</b> (Dist: ${res.distance})`
  } else if (res.path && ['bfs', 'dfs'].includes(currentAlgo)) {
    const labels = res.path.map((id) => nodes.find((n) => n.id === id).label)
    msg = `${prettyAlgo} Order: <b>${labels.join(' → ')}</b>`
  } else if (res.mst_edges) {
    msg = `${prettyAlgo}: Found ${res.mst_edges.length} edges.`
  } else if (res.max_flow !== undefined) {
    msg = `Max Flow: ${res.max_flow}`
    setNotification(msg, 'max_flow')
    return
  } else if (['fleury', 'hierholzer'].includes(currentAlgo) && res.path) {
    const type = res.euler_type || 'Path'
    const labels = res.path.map((id) => {
      const node = nodes.find((n) => n.id === id)
      return node ? node.label : id
    })
    msg = `Euler <b>${type}</b>: ${labels.join(' → ')}`
    setNotification(msg, 'max_flow')
    return
  } else if (res.is_bipartite !== undefined) {
    msg = res.is_bipartite ? ' Graph IS Bipartite' : ' Graph is NOT Bipartite'
  } else if (res.path) {
    msg = `${prettyAlgo} Path Found.`
  } else {
    msg = 'Algorithm Completed.'
  }
  setNotification(msg, 'success')
}
async function getRepresentation(mode) {
  const payload = { mode: mode, graph: { nodes, edges, directed: globalDirectedState } }
  const res = await fetch('/api/convert', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  const data = await res.json()
  document.getElementById('modal-overlay').style.display = 'flex'
  document.getElementById('result-text-modal').style.display = 'block'
  document.getElementById('result-textarea').value = data.text
}
