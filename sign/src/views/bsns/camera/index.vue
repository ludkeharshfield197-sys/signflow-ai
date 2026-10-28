<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
onMounted(() => router.replace('/app/workbench?mode=live'))
</script>

<template><p class="sf-sr-only">正在前往实时识别工作台</p></template>

