<template>
  <AppLayout v-if="!$route.meta.guest">
    <router-view />
  </AppLayout>
  <router-view v-else />
</template>

<script setup>
import AppLayout from "@/components/AppLayout.vue";
</script>

<style></style>
