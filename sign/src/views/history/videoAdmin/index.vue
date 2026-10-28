<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
const router = useRouter()
onMounted(() => router.replace('/app/results?mode=video'))
</script>
<template><p class="sf-sr-only">正在前往视频识别结果</p></template>

