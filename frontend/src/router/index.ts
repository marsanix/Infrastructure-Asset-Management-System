import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    // ── Public Landing Page ───────────────────────────────────
    {
      path: '/',
      name: 'Landing',
      component: () => import('@/views/LandingView.vue'),
      meta: { requiresAuth: false },
    },

    // ── Auth ──────────────────────────────────────────────────
    {
      path: '/login',
      name: 'Login',
      component: () => import('@/views/auth/LoginView.vue'),
      meta: { requiresAuth: false },
    },

    // ── App Shell (protected) ─────────────────────────────────
    {
      path: '/app',
      component: () => import('@/layouts/AppLayout.vue'),
      meta: { requiresAuth: true },
      children: [
        { path: '',          name: 'Dashboard',   component: () => import('@/views/DashboardView.vue') },

        // Asset Management
        { path: 'assets',          name: 'Assets',      component: () => import('@/views/assets/AssetListView.vue') },
        { path: 'assets/new',      name: 'AssetCreate', component: () => import('@/views/assets/AssetFormView.vue') },
        { path: 'assets/:id',      name: 'AssetDetail', component: () => import('@/views/assets/AssetDetailView.vue') },
        { path: 'assets/:id/edit', name: 'AssetEdit',   component: () => import('@/views/assets/AssetFormView.vue') },

        // Master Data
        { path: 'employees',   name: 'Employees',   component: () => import('@/views/master/EmployeeListView.vue') },
        { path: 'departments', name: 'Departments', component: () => import('@/views/master/DepartmentListView.vue') },
        { path: 'locations',   name: 'Locations',   component: () => import('@/views/master/LocationListView.vue') },
        { path: 'categories',  name: 'Categories',  component: () => import('@/views/master/CategoryListView.vue') },
        { path: 'brands',      name: 'Brands',      component: () => import('@/views/master/BrandListView.vue') },
        { path: 'models',      name: 'Models',      component: () => import('@/views/master/ModelListView.vue') },

        // ITSM
        { path: 'incidents',      name: 'Incidents',      component: () => import('@/views/itsm/IncidentListView.vue') },
        { path: 'incidents/:id',  name: 'IncidentDetail', component: () => import('@/views/itsm/IncidentListView.vue') },
        { path: 'changes',        name: 'Changes',        component: () => import('@/views/itsm/ChangeListView.vue') },
        { path: 'changes/:id',    name: 'ChangeDetail',   component: () => import('@/views/itsm/ChangeListView.vue') },
        { path: 'problems',       name: 'Problems',       component: () => import('@/views/itsm/ProblemListView.vue') },
        { path: 'problems/:id',   name: 'ProblemDetail',  component: () => import('@/views/itsm/ProblemListView.vue') },
        { path: 'requests',       name: 'Requests',       component: () => import('@/views/itsm/RequestListView.vue') },
        { path: 'requests/:id',   name: 'RequestDetail',  component: () => import('@/views/itsm/RequestListView.vue') },

        // Admin
        { path: 'accounts',   name: 'Accounts',  component: () => import('@/views/admin/AccountListView.vue'), meta: { permission: 'account:read' } },
        { path: 'audit-logs', name: 'AuditLogs', component: () => import('@/views/admin/AuditLogView.vue'),   meta: { permission: 'audit:read' } },
        { path: 'reports',    name: 'Reports',   component: () => import('@/views/ReportView.vue') },
      ],
    },

    // 404
    { path: '/:pathMatch(.*)*', name: 'NotFound', component: () => import('@/views/NotFoundView.vue') },
  ],
})

// ── Navigation Guard ──────────────────────────────────────────
// Gunakan flag untuk track apakah initSession sudah selesai
let sessionInitialized = false

router.beforeEach(async (to) => {
  const auth = useAuthStore()

  // Tunggu initSession selesai sebelum cek auth (hanya sekali saat pertama load)
  if (!sessionInitialized) {
    sessionInitialized = true
    await auth.initSession()
  }

  if (to.meta.requiresAuth !== false && !auth.isAuthenticated) {
    return { name: 'Login', query: { redirect: to.fullPath } }
  }

  // Sudah login dan akses /login → redirect ke dashboard app
  if (to.name === 'Login' && auth.isAuthenticated) {
    return { name: 'Dashboard' }
  }

  if (to.meta.permission && !auth.hasPermission(to.meta.permission as string)) {
    return { name: 'Dashboard' }
  }
})

export default router
