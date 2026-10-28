<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
const router = useRouter()
onMounted(() => router.replace('/app/models'))
</script>
<template><p class="sf-sr-only">正在前往模型中心</p></template>

