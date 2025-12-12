<template>
  <div class="h-screen flex flex-col bg-gray-50 dark:bg-app transition-colors duration-300 font-sans overflow-hidden">
    <NavBar />

    <div class="flex-1 w-full h-full relative cursor-move overflow-hidden">
      <!-- Legend (Positioned absolutely over graph) -->
      <div class="absolute top-4 left-4 z-10 pointer-events-auto bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm px-4 py-2 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 text-sm text-gray-500 dark:text-gray-400">
        <span class="flex items-center gap-2">
          <span class="w-3 h-3 rounded-full bg-indigo-500"></span> Memory
          <span class="w-3 h-3 rounded-full bg-emerald-500 ml-2"></span> Tag
          <span class="w-3 h-3 rounded-full bg-gray-400 ml-2"></span> Document
        </span>
      </div>

    <!-- Graph Container -->
    <div ref="container" class="w-full h-full">
      <div v-if="loading" class="absolute inset-0 flex items-center justify-center bg-white/80 dark:bg-gray-900/80 z-20 backdrop-blur-sm">
        <div class="flex flex-col items-center">
          <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mb-4"></div>
          <p class="text-gray-500 dark:text-gray-400 animate-pulse">Mapping your brain...</p>
        </div>
      </div>
      <svg ref="svg" class="w-full h-full block"></svg>
    </div>

    <!-- Zoom Controls -->
    <div class="absolute bottom-6 right-6 flex flex-col gap-2 z-10">
      <button @click="handleZoomIn" class="p-2 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" /></svg>
      </button>
      <button @click="handleZoomOut" class="p-2 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 12H4" /></svg>
      </button>
      <button @click="handleResetZoom" class="p-2 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors" title="Reset View">
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" /></svg>
      </button>
    </div>

    <!-- Tooltip -->
    <div ref="tooltip" class="fixed pointer-events-none opacity-0 transition-opacity duration-200 z-50 bg-gray-900/90 text-white px-3 py-2 rounded-lg text-sm shadow-xl backdrop-blur-sm max-w-xs transform -translate-x-1/2 -translate-y-full mt-[-10px]">
      <div class="font-semibold mb-1" ref="tooltipTitle"></div>
      <div class="text-xs text-gray-300 capitalize" ref="tooltipType"></div>
    </div>
  </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue';
import * as d3 from 'd3';
import api from '../services/api';
import { useRouter } from 'vue-router';
import { useThemeStore } from '../stores/theme';
import NavBar from '../components/NavBar.vue';

const container = ref(null);
const svg = ref(null);
const tooltip = ref(null);
const tooltipTitle = ref(null);
const tooltipType = ref(null);
const loading = ref(true);
const router = useRouter();
const themeStore = useThemeStore();

const width = ref(0);
const height = ref(0);
let simulation = null;
let zoomBehavior = null;
let svgSelection = null;
let g = null; // Main group for zoom

const fetchData = async () => {
  try {
    const response = await api.get('/memory/');
    return response.data;
  } catch (error) {
    console.error('Error fetching memories:', error);
    return [];
  }
};

const processData = (memories) => {
  const nodes = [];
  const links = [];
  const tagMap = new Map();

  memories.forEach(mem => {
    nodes.push({
      id: mem.id,
      title: mem.title,
      type: mem.type,
      radius: mem.type === 'memory' ? 25 : 20,
      group: 1
    });

    if (mem.tags && Array.isArray(mem.tags)) {
      mem.tags.forEach(tag => {
        if (!tagMap.has(tag)) {
          tagMap.set(tag, {
            id: `tag_${tag}`,
            title: tag,
            type: 'tag',
            radius: 18,
            group: 2
          });
          nodes.push(tagMap.get(tag));
        }
        
        links.push({
          source: mem.id,
          target: `tag_${tag}`,
          value: 1
        });
      });
    }
  });

  return { nodes, links };
};

const initGraph = async () => {
  loading.value = true;
  const memories = await fetchData();
  const data = processData(memories);
  loading.value = false;

  if (!container.value || !svg.value) return;

  width.value = container.value.clientWidth;
  height.value = container.value.clientHeight;

  svgSelection = d3.select(svg.value);
  svgSelection.selectAll("*").remove();

  // Define gradients and filters
  const defs = svgSelection.append("defs");

  // Drop shadow filter
  const filter = defs.append("filter")
    .attr("id", "drop-shadow")
    .attr("height", "130%");
  filter.append("feGaussianBlur")
    .attr("in", "SourceAlpha")
    .attr("stdDeviation", 3)
    .attr("result", "blur");
  filter.append("feOffset")
    .attr("in", "blur")
    .attr("dx", 2)
    .attr("dy", 2)
    .attr("result", "offsetBlur");
  filter.append("feFlood")
    .attr("flood-color", "#000")
    .attr("flood-opacity", 0.2)
    .attr("result", "offsetColor");
  filter.append("feComposite")
    .attr("in", "offsetColor")
    .attr("in2", "offsetBlur")
    .attr("operator", "in")
    .attr("result", "offsetBlur");
  filter.append("feMerge")
    .append("feMergeNode")
    .attr("in", "offsetBlur")
    .select(function() { return this.parentNode; })
    .append("feMergeNode")
    .attr("in", "SourceGraphic");

  // Gradients
  const createGradient = (id, color1, color2) => {
    const gradient = defs.append("linearGradient")
      .attr("id", id)
      .attr("x1", "0%")
      .attr("y1", "0%")
      .attr("x2", "100%")
      .attr("y2", "100%");
    gradient.append("stop").attr("offset", "0%").attr("stop-color", color1);
    gradient.append("stop").attr("offset", "100%").attr("stop-color", color2);
  };

  if (themeStore.isDark) {
    createGradient("grad-memory", "#6366f1", "#4338ca"); // Indigo
    createGradient("grad-tag", "#10b981", "#059669");    // Emerald
    createGradient("grad-doc", "#9ca3af", "#4b5563");    // Gray
  } else {
    createGradient("grad-memory", "#818cf8", "#4f46e5");
    createGradient("grad-tag", "#34d399", "#059669");
    createGradient("grad-doc", "#d1d5db", "#6b7280");
  }

  // Zoom setup
  g = svgSelection.append("g");
  zoomBehavior = d3.zoom()
    .scaleExtent([0.1, 4])
    .on("zoom", (event) => {
      g.attr("transform", event.transform);
    });
  svgSelection.call(zoomBehavior);

  // Simulation setup
  simulation = d3.forceSimulation(data.nodes)
    .force("link", d3.forceLink(data.links).id(d => d.id).distance(120))
    .force("charge", d3.forceManyBody().strength(-400))
    .force("center", d3.forceCenter(width.value / 2, height.value / 2))
    .force("collide", d3.forceCollide().radius(d => d.radius + 10).iterations(2));

  // Links
  const link = g.append("g")
    .attr("stroke", themeStore.isDark ? "#4b5563" : "#e5e7eb")
    .attr("stroke-opacity", 0.6)
    .selectAll("line")
    .data(data.links)
    .join("line")
    .attr("stroke-width", 1.5)
    .attr("class", "link transition-opacity duration-300");

  // Nodes
  const node = g.append("g")
    .selectAll("g")
    .data(data.nodes)
    .join("g")
    .attr("class", "node cursor-pointer")
    .call(drag(simulation));

  // Node circles
  node.append("circle")
    .attr("r", d => d.radius)
    .attr("fill", d => {
      if (d.type === 'tag') return "url(#grad-tag)";
      if (d.type === 'memory') return "url(#grad-memory)";
      return "url(#grad-doc)";
    })
    .attr("stroke", "#fff")
    .attr("stroke-width", 2)
    .style("filter", "url(#drop-shadow)")
    .attr("class", "transition-all duration-300");

  // Icons/Text inside nodes
  node.append("text")
    .attr("dy", d => d.type === 'tag' ? 4 : 5)
    .attr("text-anchor", "middle")
    .attr("fill", "white")
    .style("font-family", "sans-serif")
    .style("font-size", d => d.type === 'tag' ? "10px" : "14px")
    .style("pointer-events", "none")
    .text(d => {
      if (d.type === 'tag') return '#';
      if (d.type === 'memory') return 'M';
      return 'D';
    });

  // Labels (only visible on hover or zoom level?) - Let's keep them always visible but styled nicely
  const labels = g.append("g")
    .selectAll("text")
    .data(data.nodes)
    .join("text")
    .attr("dx", d => d.radius + 8)
    .attr("dy", ".35em")
    .text(d => d.title.length > 20 ? d.title.substring(0, 20) + '...' : d.title)
    .attr("fill", themeStore.isDark ? "#e5e7eb" : "#374151")
    .style("font-size", "12px")
    .style("font-weight", "500")
    .style("pointer-events", "none")
    .style("text-shadow", themeStore.isDark ? "2px 2px 4px rgba(0,0,0,0.8)" : "2px 2px 4px rgba(255,255,255,0.8)")
    .style("opacity", 0.8);

  // Interactions
  node
    .on("mouseover", (event, d) => {
      // Highlight connected
      const connectedNodeIds = new Set();
      connectedNodeIds.add(d.id);
      
      link.style("stroke", l => {
        if (l.source.id === d.id || l.target.id === d.id) {
          connectedNodeIds.add(l.source.id);
          connectedNodeIds.add(l.target.id);
          return themeStore.isDark ? "#818cf8" : "#4f46e5";
        }
        return themeStore.isDark ? "#4b5563" : "#e5e7eb";
      })
      .style("stroke-opacity", l => (l.source.id === d.id || l.target.id === d.id) ? 1 : 0.1);

      node.style("opacity", n => connectedNodeIds.has(n.id) ? 1 : 0.1);
      labels.style("opacity", n => connectedNodeIds.has(n.id) ? 1 : 0.1);

      // Tooltip
      if (tooltip.value) {
        tooltip.value.style.opacity = 1;
        tooltip.value.style.left = `${event.clientX}px`;
        tooltip.value.style.top = `${event.clientY}px`;
        tooltipTitle.value.textContent = d.title;
        tooltipType.value.textContent = d.type;
      }
    })
    .on("mouseout", () => {
      // Reset styles
      link.style("stroke", themeStore.isDark ? "#4b5563" : "#e5e7eb")
          .style("stroke-opacity", 0.6);
      node.style("opacity", 1);
      labels.style("opacity", 0.8);
      
      if (tooltip.value) {
        tooltip.value.style.opacity = 0;
      }
    })
    .on("click", (event, d) => {
      if (d.type === 'memory' || d.type === 'document') {
        const idParts = d.id.toString().split('_');
        const realId = idParts.length > 1 ? idParts[1] : d.id;
        router.push(`/editor/${d.id}`);
      }
    });

  simulation.on("tick", () => {
    link
      .attr("x1", d => d.source.x)
      .attr("y1", d => d.source.y)
      .attr("x2", d => d.target.x)
      .attr("y2", d => d.target.y);

    node.attr("transform", d => `translate(${d.x},${d.y})`);
    labels.attr("x", d => d.x).attr("y", d => d.y);
  });
};

const drag = (simulation) => {
  function dragstarted(event) {
    if (!event.active) simulation.alphaTarget(0.3).restart();
    event.subject.fx = event.subject.x;
    event.subject.fy = event.subject.y;
  }

  function dragged(event) {
    event.subject.fx = event.x;
    event.subject.fy = event.y;
  }

  function dragended(event) {
    if (!event.active) simulation.alphaTarget(0);
    event.subject.fx = null;
    event.subject.fy = null;
  }

  return d3.drag()
    .on("start", dragstarted)
    .on("drag", dragged)
    .on("end", dragended);
}

// Zoom Controls
const handleZoomIn = () => {
  if (svgSelection && zoomBehavior) {
    svgSelection.transition().duration(300).call(zoomBehavior.scaleBy, 1.2);
  }
};

const handleZoomOut = () => {
  if (svgSelection && zoomBehavior) {
    svgSelection.transition().duration(300).call(zoomBehavior.scaleBy, 0.8);
  }
};

const handleResetZoom = () => {
  if (svgSelection && zoomBehavior) {
    svgSelection.transition().duration(750).call(zoomBehavior.transform, d3.zoomIdentity);
  }
};

onMounted(() => {
  initGraph();
  window.addEventListener('resize', initGraph);
});

onUnmounted(() => {
  window.removeEventListener('resize', initGraph);
  if (simulation) simulation.stop();
});

watch(() => themeStore.isDark, () => {
  initGraph();
});
</script>

<style scoped>
.node circle {
  transition: all 0.3s ease;
}
.node:hover circle {
  stroke: #fff;
  stroke-width: 3px;
  filter: drop-shadow(0 0 8px rgba(99, 102, 241, 0.5));
}
</style>
