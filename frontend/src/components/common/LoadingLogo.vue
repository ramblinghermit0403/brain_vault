<template>
  <div class="flex items-center justify-center">
    <img 
      src="/image.svg" 
      alt="Loading..." 
      :class="[sizeClass, 'animate-custom-spin']"
    />
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  size: {
    type: String,
    default: 'md' // sm, md, lg, xl
  }
});

const sizeClass = computed(() => {
  switch (props.size) {
    case 'xs': return 'w-3 h-3';
    case 'sm': return 'w-4 h-4';
    case 'base': return 'w-5 h-5';
    case 'md': return 'w-6 h-6';
    case 'lg': return 'w-10 h-10';
    case 'xl': return 'w-14 h-14';
    default: return 'w-6 h-6';
  }
});
</script>

<style scoped>
@keyframes custom-spin {
  0% { transform: rotate(0deg); }
  50% { transform: rotate(180deg); } /* Slowing down here? or just standard spin? User aid "slow stop and gain start" */
  /* "Slow stop and gain start" usually implies an ease-in-out or similar curve where it moves, slows down (stops), then speeds up again. 
     Let's use a cubic-bezier for a sharp "spin, stop, spin" feel. 
  */
  100% { transform: rotate(360deg); }
}

.animate-custom-spin {
  /* cubic-bezier(0.4, 0, 0.2, 1) is standard ease-in-out. 
     For "slow stop", we might want something that hangs at the top.
     Let's try a custom bezier that emphasizes the slow part.
  */
  animation: custom-spin 2s cubic-bezier(0.68, -0.55, 0.265, 1.55) infinite; 
  /* Actually, maybe just a standard ease-in-out is closer to "slow stop, gain start" if we interpret it as:
     Starts slow (gain start?), speeds up, slows to a stop.
     Or "Gain start" = fast start?
     "Slow stop" = slows down at end.
     "Gain start" = speeds up at start.
     This sounds like Ease-In-Out.
     Let's try a distinct ease-in-out.
  */
  animation: custom-spin 1.5s cubic-bezier(0.45, 0, 0.55, 1) infinite;
}
</style>
