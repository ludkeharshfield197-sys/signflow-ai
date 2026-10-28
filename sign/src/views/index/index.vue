<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
const router = useRouter()
onMounted(() => router.replace('/app/overview'))
</script>
<template><p class="sf-sr-only">正在前往产品概览</p></template>

