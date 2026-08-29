<template>
  <aside class="sidebar" :class="{ collapsed }">
    <div class="sidebar-header">
      <div class="logo" :class="{ collapsed }">
        <span class="logo-mark">{{ logoInitial }}</span>
        <div v-if="!collapsed" class="logo-text">
          <h1>{{ t('nav.companyName') }}</h1>
          <span class="subtitle">{{ t('nav.subtitle') }}</span>
        </div>
      </div>
      <button
        class="collapse-toggle"
        @click="toggleCollapsed"
        :title="collapsed ? 'Expand sidebar' : 'Collapse sidebar'"
      >
        <svg width="18" height="18" viewBox="0 0 18 18" fill="none" :class="{ flipped: collapsed }">
          <path d="M11.5 4L6.5 9L11.5 14" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </button>
    </div>

    <nav class="nav-list">
      <router-link
        v-for="item in navItems"
        :key="item.path"
        :to="item.path"
        class="nav-item"
        :class="{ active: $route.path === item.path }"
        :data-tooltip="item.label"
      >
        <span class="nav-icon" v-html="item.icon"></span>
        <span v-if="!collapsed" class="nav-label">{{ item.label }}</span>
      </router-link>
    </nav>

    <div class="sidebar-footer">
      <LanguageSwitcher :collapsed="collapsed" />
      <ProfileMenu
        :collapsed="collapsed"
        @show-profile-details="$emit('show-profile-details')"
        @show-tasks="$emit('show-tasks')"
      />
    </div>
  </aside>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useI18n } from '../composables/useI18n'
import ProfileMenu from './ProfileMenu.vue'
import LanguageSwitcher from './LanguageSwitcher.vue'

defineEmits(['show-profile-details', 'show-tasks'])

const { t } = useI18n()

const STORAGE_KEY = 'sidebarCollapsed'
const MEDIA_QUERY = '(max-width: 1024px)'

const collapsed = ref(false)
let mediaQuery = null
let hasManualOverride = false

const handleMediaQueryChange = (e) => {
  if (hasManualOverride) return
  collapsed.value = e.matches
}

onMounted(() => {
  mediaQuery = window.matchMedia(MEDIA_QUERY)

  const stored = localStorage.getItem(STORAGE_KEY)
  if (stored !== null) {
    hasManualOverride = true
    collapsed.value = stored === 'true'
  } else {
    collapsed.value = mediaQuery.matches
  }

  mediaQuery.addEventListener('change', handleMediaQueryChange)
})

onUnmounted(() => {
  if (mediaQuery) {
    mediaQuery.removeEventListener('change', handleMediaQueryChange)
  }
})

const toggleCollapsed = () => {
  collapsed.value = !collapsed.value
  hasManualOverride = true
  localStorage.setItem(STORAGE_KEY, String(collapsed.value))
}

const logoInitial = computed(() => {
  const name = t('nav.companyName')
  return name ? name.charAt(0).toUpperCase() : 'F'
})

const icons = {
  overview: '<svg width="20" height="20" viewBox="0 0 20 20" fill="none"><rect x="3" y="3" width="6" height="6" rx="1" stroke="currentColor" stroke-width="1.5"/><rect x="11" y="3" width="6" height="6" rx="1" stroke="currentColor" stroke-width="1.5"/><rect x="3" y="11" width="6" height="6" rx="1" stroke="currentColor" stroke-width="1.5"/><rect x="11" y="11" width="6" height="6" rx="1" stroke="currentColor" stroke-width="1.5"/></svg>',
  inventory: '<svg width="20" height="20" viewBox="0 0 20 20" fill="none"><path d="M3 6L10 2.5L17 6L10 9.5L3 6Z" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/><path d="M3 6V14L10 17.5L17 14V6" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/><path d="M10 9.5V17.5" stroke="currentColor" stroke-width="1.5"/></svg>',
  orders: '<svg width="20" height="20" viewBox="0 0 20 20" fill="none"><path d="M4 3H16L15 13H5L4 3Z" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/><path d="M2 3H4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/><circle cx="7.5" cy="16.5" r="1.25" stroke="currentColor" stroke-width="1.5"/><circle cx="13.5" cy="16.5" r="1.25" stroke="currentColor" stroke-width="1.5"/></svg>',
  finance: '<svg width="20" height="20" viewBox="0 0 20 20" fill="none"><path d="M10 2V18" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/><path d="M14 5.5C14 5.5 12.5 4.5 10 4.5C7.5 4.5 6.5 5.75 6.5 7C6.5 10 14 9 14 13C14 14.25 12.5 15.5 10 15.5C7.5 15.5 6 14.5 6 14.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>',
  demandForecast: '<svg width="20" height="20" viewBox="0 0 20 20" fill="none"><path d="M3 15L7.5 9.5L11 12.5L17 5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/><path d="M13 5H17V9" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>',
  restocking: '<svg width="20" height="20" viewBox="0 0 20 20" fill="none"><path d="M4 3H16" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/><path d="M5 3V15C5 15.5523 5.44772 16 6 16H14C14.5523 16 15 15.5523 15 15V3" stroke="currentColor" stroke-width="1.5"/><path d="M8 8L10 10L12 8" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/><path d="M10 6V10" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>',
  reports: '<svg width="20" height="20" viewBox="0 0 20 20" fill="none"><rect x="3" y="2.5" width="14" height="15" rx="1" stroke="currentColor" stroke-width="1.5"/><path d="M6.5 11.5V13.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/><path d="M10 8.5V13.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/><path d="M13.5 6V13.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>'
}

const navItems = computed(() => [
  { path: '/', label: t('nav.overview'), icon: icons.overview },
  { path: '/inventory', label: t('nav.inventory'), icon: icons.inventory },
  { path: '/orders', label: t('nav.orders'), icon: icons.orders },
  { path: '/spending', label: t('nav.finance'), icon: icons.finance },
  { path: '/demand', label: t('nav.demandForecast'), icon: icons.demandForecast },
  { path: '/restocking', label: t('nav.restocking'), icon: icons.restocking },
  { path: '/reports', label: 'Reports', icon: icons.reports }
])
</script>

<style scoped>
.sidebar {
  width: 240px;
  flex-shrink: 0;
  background: var(--color-surface, #ffffff);
  border-right: 1px solid var(--color-border, #e2e8f0);
  display: flex;
  flex-direction: column;
  position: sticky;
  top: 0;
  height: 100vh;
  z-index: 50;
  transition: width 0.2s ease;
}

.sidebar.collapsed {
  width: 72px;
}

.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-2, 0.5rem);
  padding: var(--space-5, 1.25rem) var(--space-4, 1rem);
  border-bottom: 1px solid var(--color-border, #e2e8f0);
  min-height: 70px;
}

.logo {
  display: flex;
  align-items: center;
  gap: var(--space-3, 0.75rem);
  min-width: 0;
}

.logo-mark {
  flex-shrink: 0;
  width: 32px;
  height: 32px;
  border-radius: var(--radius-md, 8px);
  background: linear-gradient(135deg, var(--color-primary, #2563eb) 0%, var(--color-primary-dark, #1e40af) 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.938rem;
}

.logo-text {
  min-width: 0;
  overflow: hidden;
}

.logo-text h1 {
  font-size: 1.125rem;
  font-weight: 700;
  color: var(--color-text, #0f172a);
  letter-spacing: -0.025em;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.subtitle {
  display: block;
  font-size: 0.75rem;
  color: var(--color-text-secondary, #64748b);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.collapse-toggle {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  background: none;
  border: 1px solid var(--color-border, #e2e8f0);
  border-radius: var(--radius-sm, 6px);
  color: var(--color-text-secondary, #64748b);
  cursor: pointer;
  transition: all 0.2s ease;
}

.collapse-toggle:hover {
  background: var(--color-border-subtle, #f1f5f9);
  color: var(--color-text, #0f172a);
}

.collapse-toggle svg {
  transition: transform 0.2s ease;
}

.collapse-toggle svg.flipped {
  transform: rotate(180deg);
}

.nav-list {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-4, 1rem) var(--space-3, 0.75rem);
  display: flex;
  flex-direction: column;
  gap: var(--space-1, 0.25rem);
}

.nav-item {
  display: flex;
  align-items: center;
  gap: var(--space-3, 0.75rem);
  padding: 0.625rem var(--space-3, 0.75rem);
  color: var(--color-text-secondary, #64748b);
  text-decoration: none;
  font-weight: 500;
  font-size: 0.938rem;
  border-radius: var(--radius-sm, 6px);
  transition: all 0.2s ease;
  position: relative;
  white-space: nowrap;
}

.sidebar.collapsed .nav-item {
  justify-content: center;
  padding: 0.625rem;
}

.nav-item:hover {
  color: var(--color-text, #0f172a);
  background: var(--color-border-subtle, #f1f5f9);
}

.nav-item.active {
  color: var(--color-primary, #2563eb);
  background: var(--color-primary-bg, #eff6ff);
}

.nav-icon {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.nav-label {
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Tooltip for collapsed icon-only nav items */
.sidebar.collapsed .nav-item[data-tooltip]:hover::after {
  content: attr(data-tooltip);
  position: absolute;
  left: calc(100% + 0.5rem);
  top: 50%;
  transform: translateY(-50%);
  background: var(--color-text, #0f172a);
  color: white;
  padding: 0.375rem 0.625rem;
  border-radius: var(--radius-sm, 6px);
  font-size: 0.813rem;
  font-weight: 500;
  white-space: nowrap;
  z-index: 60;
  pointer-events: none;
}

.sidebar-footer {
  border-top: 1px solid var(--color-border, #e2e8f0);
  padding: var(--space-3, 0.75rem);
  display: flex;
  flex-direction: column;
  gap: var(--space-2, 0.5rem);
}

.sidebar.collapsed .sidebar-footer {
  align-items: center;
}
</style>
