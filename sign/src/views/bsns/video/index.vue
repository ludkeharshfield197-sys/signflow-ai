<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
onMounted(() => router.replace('/app/workbench?mode=video'))
</script>

<template><p class="sf-sr-only">正在前往视频识别工作台</p></template>

