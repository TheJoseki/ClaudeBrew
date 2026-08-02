# Coding Convention — [PROJECT_NAME]

> **Version**: 1.0
> **Applies to**: [BACKEND_FRAMEWORK] Backend + [FRONTEND_FRAMEWORK] Frontend
> **Reference**: `docs/CODING_RULES.md` (enforcement rules), `docs/ARCHITECTURE.md` (system design)
> Copy from `docs/_templates/CODING_CONVENTION.md` to `docs/CODING_CONVENTION.md` and fill in per project.

---

## 1. Project Structure Convention

### 1.1 Backend ([BACKEND_FRAMEWORK])

**NestJS example structure:**
```
backend/
├── src/
│   ├── common/                         # ── Shared infrastructure ──
│   │   ├── constants/
│   │   │   ├── app.constants.ts        # MAX_FILE_SIZE, DEFAULT_PAGE_SIZE, etc.
│   │   │   └── status.enum.ts          # [EntityStatus], [RoleCode] enums
│   │   ├── decorators/
│   │   │   ├── current-user.decorator.ts   # @CurrentUser()
│   │   │   └── roles.decorator.ts          # @Roles('[role1]', '[role2]')
│   │   ├── dto/
│   │   │   ├── pagination.dto.ts           # PaginationDto (page, pageSize)
│   │   │   └── base-response.dto.ts        # BaseResponseDto
│   │   ├── filters/
│   │   │   └── http-exception.filter.ts    # Global exception filter
│   │   ├── guards/
│   │   │   ├── jwt-auth.guard.ts           # JwtAuthGuard
│   │   │   └── roles.guard.ts              # RolesGuard
│   │   ├── interceptors/
│   │   │   ├── audit.interceptor.ts        # Auto-set audit columns
│   │   │   └── transform.interceptor.ts    # Standard response wrapper
│   │   └── pipes/
│   │       └── validation.pipe.ts          # Global validation pipe
│   │
│   ├── modules/                        # ── Feature modules ──
│   │   ├── auth/
│   │   │   ├── auth.module.ts
│   │   │   ├── auth.controller.ts
│   │   │   ├── auth.service.ts
│   │   │   ├── dto/
│   │   │   │   ├── login.dto.ts
│   │   │   │   └── refresh-token.dto.ts
│   │   │   ├── strategies/
│   │   │   │   └── jwt.strategy.ts
│   │   │   └── auth.spec.ts
│   │   │
│   │   ├── <module>/                   # [CUSTOMIZE: add feature modules]
│   │   │   ├── <module>.module.ts
│   │   │   ├── <module>.controller.ts
│   │   │   ├── <module>.service.ts
│   │   │   ├── dto/
│   │   │   │   ├── create-<module>.dto.ts
│   │   │   │   ├── update-<module>.dto.ts
│   │   │   │   └── query-<module>.dto.ts
│   │   │   └── <module>.spec.ts
│   │   │
│   │   └── [OTHER_MODULES]/            # e.g. users/, companies/, files/
│   │
│   ├── prisma/
│   │   └── prisma.service.ts           # PrismaService extends PrismaClient
│   ├── app.module.ts
│   └── main.ts
│
├── prisma/
│   ├── schema.prisma
│   ├── seed.ts
│   └── migrations/
├── test/                               # E2E tests
│   └── app.e2e-spec.ts
├── .env.example
├── nest-cli.json
├── tsconfig.json
└── package.json
```

### 1.2 Frontend ([FRONTEND_FRAMEWORK])

**Vue.js 3 example structure:**
```
frontend/
├── public/
│   └── favicon.ico
├── src/
│   ├── assets/                         # ── Static resources ──
│   │   ├── images/
│   │   ├── styles/
│   │   │   └── variables.scss          # UI framework theme overrides
│   │   └── fonts/
│   │
│   ├── components/                     # ── Reusable UI components ──
│   │   ├── common/                     # Shared across modules
│   │   │   ├── AppHeader.vue
│   │   │   ├── NavDrawer.vue
│   │   │   ├── StatusBadge.vue
│   │   │   ├── ConfirmDialog.vue
│   │   │   ├── DataTableServer.vue
│   │   │   ├── SearchToolbar.vue
│   │   │   ├── EmptyState.vue
│   │   │   └── BreadcrumbNav.vue
│   │   └── <module>/                   # [CUSTOMIZE: module components]
│   │       └── <ModuleComponent>.vue
│   │
│   ├── composables/                    # ── Shared logic (hooks) ──
│   │   ├── useAuth.ts
│   │   ├── usePagination.ts
│   │   ├── useNotification.ts
│   │   └── usePermission.ts
│   │
│   ├── layouts/                        # ── Layout shells ──
│   │   ├── MainLayout.vue
│   │   └── AuthLayout.vue
│   │
│   ├── locales/                        # ── i18n messages ──
│   │   ├── [LANG_1].json              # [CUSTOMIZE: primary language]
│   │   └── [LANG_2].json              # [CUSTOMIZE: secondary language]
│   │
│   ├── mock/                           # ── Prototype fake data ──
│   │   ├── [entity1].ts
│   │   └── [entity2].ts
│   │
│   ├── plugins/                        # ── Plugin setup ──
│   │   ├── vuetify.ts
│   │   ├── i18n.ts
│   │   └── pinia.ts
│   │
│   ├── router/
│   │   └── index.ts                   # Routes + auth/role guards
│   │
│   ├── services/                       # ── API services ──
│   │   ├── api.ts                     # Axios instance + interceptor
│   │   ├── auth.service.ts
│   │   └── <module>.service.ts
│   │
│   ├── stores/                         # ── Pinia stores ──
│   │   ├── auth.ts
│   │   ├── ui.ts
│   │   └── <module>.ts
│   │
│   ├── types/                          # ── TypeScript interfaces ──
│   │   ├── auth.ts
│   │   ├── common.ts                  # PaginatedResponse, ApiResponse, etc.
│   │   └── <module>.ts
│   │
│   ├── views/                          # ── Page-level components ──
│   │   ├── auth/
│   │   │   ├── LoginView.vue
│   │   │   └── ForgotPasswordView.vue
│   │   ├── dashboard/
│   │   │   └── DashboardView.vue
│   │   └── <module>/
│   │       ├── <Module>ListView.vue
│   │       └── <Module>DetailView.vue
│   │
│   ├── App.vue
│   └── main.ts
│
├── __tests__/                          # ── Test files ──
│   ├── setup.ts
│   ├── stores/
│   ├── components/
│   ├── views/
│   └── integration/
│
├── index.html
├── vite.config.ts
├── vitest.config.ts
├── tsconfig.json
└── package.json
```

---

## 2. Backend Coding Convention

### 2.1 Module Template

```typescript
// modules/<module>/<module>.module.ts
import { Module } from '@nestjs/common';
import { FeatureController } from './<module>.controller';
import { FeatureService } from './<module>.service';
import { PrismaModule } from '../../prisma/prisma.module';

@Module({
  imports: [PrismaModule],
  controllers: [FeatureController],
  providers: [FeatureService],
  exports: [FeatureService],
})
export class FeatureModule {}
```

### 2.2 Controller Template

```typescript
// modules/<module>/<module>.controller.ts
import { Controller, Get, Post, Patch, Delete, Query, Param, Body, UseGuards } from '@nestjs/common';
import { ApiTags, ApiBearerAuth, ApiOperation, ApiResponse } from '@nestjs/swagger';
import { JwtAuthGuard } from '../../common/guards/jwt-auth.guard';
import { RolesGuard } from '../../common/guards/roles.guard';
import { Roles } from '../../common/decorators/roles.decorator';
import { CurrentUser } from '../../common/decorators/current-user.decorator';
import { FeatureService } from './<module>.service';
import { QueryFeatureDto } from './dto/query-<module>.dto';
import { CreateFeatureDto } from './dto/create-<module>.dto';
import type { UserPayload } from '../../common/types';

@ApiTags('<module>')
@ApiBearerAuth()
@UseGuards(JwtAuthGuard, RolesGuard)
@Controller('api/v1/<module>')
export class FeatureController {
  constructor(private readonly featureService: FeatureService) {}

  @Get()
  @Roles('[role1]', '[role2]')
  @ApiOperation({ summary: 'List [entities]' })
  async findAll(
    @Query() query: QueryFeatureDto,
    @CurrentUser() user: UserPayload,
  ) {
    return this.featureService.findAll(query, user);
  }

  @Post()
  @Roles('[role1]')
  @ApiOperation({ summary: 'Create [entity]' })
  async create(
    @Body() dto: CreateFeatureDto,
    @CurrentUser() user: UserPayload,
  ) {
    return this.featureService.create(dto, user);
  }

  @Patch(':id')
  @Roles('[role1]', '[role2]')
  @ApiOperation({ summary: 'Update [entity]' })
  async update(
    @Param('id') id: number,
    @Body() dto: UpdateFeatureDto,
    @CurrentUser() user: UserPayload,
  ) {
    return this.featureService.update(id, dto, user);
  }

  @Delete(':id')
  @Roles('[role1]')
  @ApiOperation({ summary: 'Soft delete [entity]' })
  async remove(
    @Param('id') id: number,
    @CurrentUser() user: UserPayload,
  ) {
    return this.featureService.remove(id, user);
  }
}
```

### 2.3 Service Template

```typescript
// modules/<module>/<module>.service.ts
import { Injectable, HttpException, HttpStatus } from '@nestjs/common';
import { PrismaService } from '../../prisma/prisma.service';
import { QueryFeatureDto } from './dto/query-<module>.dto';
import { CreateFeatureDto } from './dto/create-<module>.dto';
import type { UserPayload } from '../../common/types';
import type { Prisma } from '@prisma/client';

@Injectable()
export class FeatureService {
  constructor(private readonly prisma: PrismaService) {}

  async findAll(query: QueryFeatureDto, user: UserPayload) {
    const { page = 1, pageSize = 20, search } = query;

    const where: Prisma.FeatureWhereInput = {
      DeleteFlag: '0',                    // [CUSTOMIZE: soft delete filter]
      ...(search && {
        Name: { contains: search, mode: 'insensitive' },
      }),
    };

    const [results, count] = await Promise.all([
      this.prisma.feature.findMany({
        where,
        skip: (page - 1) * pageSize,
        take: pageSize,
        include: {
          // [CUSTOMIZE: include related data]
        },
        orderBy: { CreateDate: 'desc' },
      }),
      this.prisma.feature.count({ where }),
    ]);

    return {
      results,
      count,
      page,
      pageSize,
      totalPages: Math.ceil(count / pageSize),
    };
  }

  async create(dto: CreateFeatureDto, user: UserPayload) {
    return this.prisma.feature.create({
      data: {
        ...dto,
        DeleteFlag: '0',
        CreateBy: user.id,
        CreateDate: new Date(),
      },
    });
  }

  async findOne(id: number) {
    const record = await this.prisma.feature.findFirst({
      where: { id, DeleteFlag: '0' },
    });
    if (!record) {
      throw new HttpException('[Entity] not found', HttpStatus.NOT_FOUND);
    }
    return record;
  }

  async update(id: number, dto: UpdateFeatureDto, user: UserPayload) {
    await this.findOne(id);
    return this.prisma.feature.update({
      where: { id },
      data: {
        ...dto,
        UpdateBy: user.id,
        UpdateDate: new Date(),
      },
    });
  }

  async remove(id: number, user: UserPayload) {
    await this.findOne(id);
    return this.prisma.feature.update({
      where: { id },
      data: {
        DeleteFlag: '1',
        UpdateBy: user.id,
        UpdateDate: new Date(),
      },
    });
  }
}
```

### 2.4 DTO Template

```typescript
// modules/<module>/dto/create-<module>.dto.ts
import { ApiProperty, ApiPropertyOptional } from '@nestjs/swagger';
import { IsNotEmpty, IsInt, IsOptional, IsString, MaxLength } from 'class-validator';
import { Type } from 'class-transformer';

export class CreateFeatureDto {
  @ApiProperty({ description: '[Field description]' })
  @IsNotEmpty({ message: '[Field] is required' })
  @IsString()
  @MaxLength(200)
  name: string;

  @ApiPropertyOptional({ description: '[Optional field description]' })
  @IsOptional()
  @IsString()
  @MaxLength(1000)
  description?: string;

  @ApiProperty({ description: '[FK description]' })
  @IsNotEmpty()
  @IsInt()
  @Type(() => Number)
  relatedId: number;
}
```

```typescript
// modules/<module>/dto/query-<module>.dto.ts
import { ApiPropertyOptional } from '@nestjs/swagger';
import { IsOptional, IsInt, IsString, Min } from 'class-validator';
import { Type } from 'class-transformer';

export class QueryFeatureDto {
  @ApiPropertyOptional({ default: 1 })
  @IsOptional()
  @IsInt()
  @Min(1)
  @Type(() => Number)
  page?: number = 1;

  @ApiPropertyOptional({ default: 20 })
  @IsOptional()
  @IsInt()
  @Min(1)
  @Type(() => Number)
  pageSize?: number = 20;

  @ApiPropertyOptional()
  @IsOptional()
  @IsString()
  search?: string;
}
```

### 2.5 ORM Schema Convention

```prisma
// prisma/schema.prisma

// [CUSTOMIZE: Model name = PascalCase, column = PascalCase (match DB)]

model Feature {
  id              Int       @id @default(autoincrement()) @map("Id")
  Name            String    @db.VarChar(200)
  Description     String?   @db.VarChar(1000)
  RelatedId       Int
  CreateBy        Int?
  CreateDate      DateTime  @default(now())
  UpdateBy        Int?
  UpdateDate      DateTime?
  DeleteFlag      String    @default("0") @db.VarChar(1)

  // Relations
  Related         RelatedModel @relation(fields: [RelatedId], references: [id])

  @@map("Feature")
}
```

---

## 3. Frontend Coding Convention

### 3.1 Component Template (View)

```vue
<!-- views/<module>/<Module>ListView.vue -->
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { useFeatureStore } from '@/stores/<module>'
import { storeToRefs } from 'pinia'
import type { DataTableHeader } from '@/types/common'

// ── i18n ──
const { t } = useI18n()
const router = useRouter()

// ── Store ──
const featureStore = useFeatureStore()
const { items, total, loading } = storeToRefs(featureStore)

// ── State ──
const page = ref(1)
const pageSize = ref(20)
const search = ref('')

// ── Computed ──
const headers = computed<DataTableHeader[]>(() => [
  { title: t('<module>.name'), key: 'name', sortable: true },
  { title: t('common.createdDate'), key: 'createdDate', sortable: true },
  { title: t('common.actions'), key: 'actions', sortable: false },
])

// ── Methods ──
async function fetchData(): Promise<void> {
  await featureStore.fetchList({
    page: page.value,
    pageSize: pageSize.value,
    search: search.value,
  })
}

function viewDetail(id: number): void {
  router.push({ name: '<Module>Detail', params: { id } })
}

// ── Lifecycle ──
onMounted(fetchData)
</script>

<template>
  <v-container fluid>
    <!-- Page Header -->
    <v-row>
      <v-col>
        <h1 class="text-h5">{{ t('<module>.listTitle') }}</h1>
      </v-col>
    </v-row>

    <!-- Search Toolbar -->
    <v-row>
      <v-col cols="12" md="4">
        <v-text-field
          v-model="search"
          :label="t('common.search')"
          prepend-inner-icon="mdi-magnify"
          clearable
          density="compact"
          variant="outlined"
          @update:model-value="fetchData"
        />
      </v-col>
    </v-row>

    <!-- Data Table -->
    <v-data-table-server
      :headers="headers"
      :items="items"
      :items-length="total"
      :loading="loading"
      :page="page"
      :items-per-page="pageSize"
      @update:page="page = $event; fetchData()"
      @update:items-per-page="pageSize = $event; fetchData()"
    >
      <template #item.actions="{ item }">
        <v-btn icon size="small" @click="viewDetail(item.id)">
          <v-icon>mdi-eye</v-icon>
        </v-btn>
      </template>

      <template #no-data>
        <v-empty-state
          :title="t('common.noData')"
          :description="t('<module>.noItems')"
          icon="mdi-file-document-outline"
        />
      </template>
    </v-data-table-server>
  </v-container>
</template>
```

### 3.2 Component Template (Reusable)

```vue
<!-- components/common/StatusBadge.vue -->
<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { EntityStatus } from '@/types/<module>'    // [CUSTOMIZE: import correct enum]

// ── Props ──
interface Props {
  status: EntityStatus
  size?: 'small' | 'default' | 'large'
}

const props = withDefaults(defineProps<Props>(), {
  size: 'default',
})

// ── i18n ──
const { t } = useI18n()

// ── Computed ──
const statusConfig = computed(() => {
  // [CUSTOMIZE: map each status to color/icon/label]
  const config: Record<EntityStatus, { color: string; icon: string; label: string }> = {
    [EntityStatus.Draft]: { color: 'grey', icon: 'mdi-file-edit-outline', label: t('status.draft') },
    [EntityStatus.Active]: { color: 'green', icon: 'mdi-check-circle', label: t('status.active') },
    [EntityStatus.Inactive]: { color: 'red', icon: 'mdi-close-circle', label: t('status.inactive') },
  }
  return config[props.status]
})
</script>

<template>
  <v-chip
    :color="statusConfig.color"
    :size="size"
    :prepend-icon="statusConfig.icon"
    variant="tonal"
  >
    {{ statusConfig.label }}
  </v-chip>
</template>
```

### 3.3 Pinia Store Template

```typescript
// stores/<module>.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { featureService } from '@/services/<module>.service'
import type { Feature, QueryParams } from '@/types/<module>'

export const useFeatureStore = defineStore('<module>', () => {
  // ── State ──
  const items = ref<Feature[]>([])
  const currentItem = ref<Feature | null>(null)
  const total = ref(0)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // ── Getters ──
  const hasItems = computed(() => items.value.length > 0)

  // ── Actions ──
  async function fetchList(params: QueryParams): Promise<void> {
    loading.value = true
    error.value = null
    try {
      const response = await featureService.getList(params)
      items.value = response.results
      total.value = response.count
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchOne(id: number): Promise<Feature> {
    loading.value = true
    error.value = null
    try {
      const item = await featureService.getOne(id)
      currentItem.value = item
      return item
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Unknown error'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function create(data: Partial<Feature>): Promise<Feature> {
    const created = await featureService.create(data)
    items.value.unshift(created)
    total.value++
    return created
  }

  async function update(id: number, data: Partial<Feature>): Promise<Feature> {
    const updated = await featureService.update(id, data)
    const index = items.value.findIndex((item) => item.id === id)
    if (index !== -1) {
      items.value[index] = updated
    }
    if (currentItem.value?.id === id) {
      currentItem.value = updated
    }
    return updated
  }

  async function remove(id: number): Promise<void> {
    await featureService.remove(id)
    items.value = items.value.filter((item) => item.id !== id)
    total.value--
  }

  function $reset(): void {
    items.value = []
    currentItem.value = null
    total.value = 0
    loading.value = false
    error.value = null
  }

  return {
    // State
    items, currentItem, total, loading, error,
    // Getters
    hasItems,
    // Actions
    fetchList, fetchOne, create, update, remove, $reset,
  }
})
```

### 3.4 API Service Template

```typescript
// services/<module>.service.ts
import api from './api'
import type { Feature, QueryParams } from '@/types/<module>'
import type { PaginatedResponse } from '@/types/common'

class FeatureService {
  private readonly baseUrl = '/api/v1/<module>'    // [CUSTOMIZE: base URL]

  async getList(params: QueryParams): Promise<PaginatedResponse<Feature>> {
    const { data } = await api.get<PaginatedResponse<Feature>>(this.baseUrl, { params })
    return data
  }

  async getOne(id: number): Promise<Feature> {
    const { data } = await api.get<Feature>(`${this.baseUrl}/${id}`)
    return data
  }

  async create(payload: Partial<Feature>): Promise<Feature> {
    const { data } = await api.post<Feature>(this.baseUrl, payload)
    return data
  }

  async update(id: number, payload: Partial<Feature>): Promise<Feature> {
    const { data } = await api.patch<Feature>(`${this.baseUrl}/${id}`, payload)
    return data
  }

  async remove(id: number): Promise<void> {
    await api.delete(`${this.baseUrl}/${id}`)
  }
}

export const featureService = new FeatureService()
```

### 3.5 TypeScript Type Template

```typescript
// types/<module>.ts

/** Entity status enum — [CUSTOMIZE per project] */
export enum EntityStatus {
  Draft = 1,
  Active = 2,
  Inactive = 3,
  // [ADD MORE STATUS VALUES]
}

/** Feature list item */
export interface Feature {
  id: number
  name: string
  description?: string
  status: EntityStatus
  createdBy: {
    id: number
    displayName: string
  }
  createdDate: string
  updatedDate: string
}

/** Feature detail (extend as needed) */
export interface FeatureDetail extends Feature {
  // [ADD detail-specific fields]
  relatedItems?: RelatedItem[]
}

/** Query params for list endpoint */
export interface QueryParams {
  page?: number
  pageSize?: number
  search?: string
  // [ADD module-specific filters]
}
```

### 3.6 Axios Instance Template

```typescript
// services/api.ts
import axios from 'axios'
import type { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from 'axios'

// [CUSTOMIZE: token storage keys]
const TOKEN_KEY = '${PROJECT_PREFIX}_access_token'
const REFRESH_KEY = '${PROJECT_PREFIX}_refresh_token'

const api: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '',
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
})

// ── Request interceptor: attach JWT ──
api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = localStorage.getItem(TOKEN_KEY)
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// ── Response interceptor: auto-refresh on 401 ──
let isRefreshing = false
let failedQueue: Array<{ resolve: (token: string) => void; reject: (error: unknown) => void }> = []

function processQueue(error: unknown, token: string | null): void {
  failedQueue.forEach(({ resolve, reject }) => {
    if (token) resolve(token)
    else reject(error)
  })
  failedQueue = []
}

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config
    if (!originalRequest || error.response?.status !== 401) {
      return Promise.reject(error)
    }

    if (isRefreshing) {
      return new Promise((resolve, reject) => {
        failedQueue.push({ resolve, reject })
      }).then((token) => {
        if (originalRequest.headers) {
          originalRequest.headers.Authorization = `Bearer ${token}`
        }
        return api(originalRequest)
      })
    }

    isRefreshing = true
    const refreshToken = localStorage.getItem(REFRESH_KEY)

    try {
      // [CUSTOMIZE: refresh endpoint]
      const { data } = await axios.post('/api/v1/auth/refresh/', { refresh: refreshToken })
      localStorage.setItem(TOKEN_KEY, data.access)
      processQueue(null, data.access)
      if (originalRequest.headers) {
        originalRequest.headers.Authorization = `Bearer ${data.access}`
      }
      return api(originalRequest)
    } catch (refreshError) {
      processQueue(refreshError, null)
      localStorage.removeItem(TOKEN_KEY)
      localStorage.removeItem(REFRESH_KEY)
      window.location.href = '/login'
      return Promise.reject(refreshError)
    } finally {
      isRefreshing = false
    }
  },
)

export default api
```

### 3.7 Router Convention

```typescript
// router/index.ts
import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  // ── Public routes (no auth) ──
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/auth/LoginView.vue'),
    meta: { requiresAuth: false, layout: 'auth' },
  },

  // ── Protected routes ──
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('@/views/dashboard/DashboardView.vue'),
    meta: { requiresAuth: true, roles: ['[role1]', '[role2]', '[role3]'] },
  },
  // [CUSTOMIZE: add routes per module]
  {
    path: '/<module>',
    name: '<Module>List',
    component: () => import('@/views/<module>/<Module>ListView.vue'),
    meta: { requiresAuth: true, roles: ['[role1]', '[role2]'] },
  },
  {
    path: '/admin/<module>',
    name: 'Admin<Module>',
    component: () => import('@/views/admin/<module>View.vue'),
    meta: { requiresAuth: true, roles: ['admin'] },   // [CUSTOMIZE: admin-only routes]
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// ── Auth guard ──
router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem(TOKEN_KEY)       // [CUSTOMIZE: TOKEN_KEY]
  const userStr = localStorage.getItem(USER_KEY)      // [CUSTOMIZE: USER_KEY]

  if (to.meta.requiresAuth && !token) {
    return next({ name: 'Login' })
  }

  if (to.meta.roles && userStr) {
    const user = JSON.parse(userStr)
    const userRoles: string[] = user.roles || []
    const allowedRoles = to.meta.roles as string[]
    if (!userRoles.some((r) => allowedRoles.includes(r))) {
      return next({ name: 'Dashboard' })             // or 403 page
    }
  }

  next()
})

export default router
```

### 3.8 i18n Convention

```json
// locales/[LANG_1].json — [CUSTOMIZE: fill with project language]
{
  "common": {
    "save": "[TRANSLATE: Save]",
    "cancel": "[TRANSLATE: Cancel]",
    "delete": "[TRANSLATE: Delete]",
    "edit": "[TRANSLATE: Edit]",
    "create": "[TRANSLATE: Create]",
    "search": "[TRANSLATE: Search]",
    "actions": "[TRANSLATE: Actions]",
    "confirm": "[TRANSLATE: Confirm]",
    "noData": "[TRANSLATE: No data]",
    "loading": "[TRANSLATE: Loading...]",
    "createdDate": "[TRANSLATE: Created date]",
    "updatedDate": "[TRANSLATE: Updated date]",
    "success": "[TRANSLATE: Success]",
    "error": "[TRANSLATE: An error occurred]"
  },
  "auth": {
    "login": "[TRANSLATE: Login]",
    "logout": "[TRANSLATE: Logout]",
    "username": "[TRANSLATE: Username]",
    "password": "[TRANSLATE: Password]",
    "forgotPassword": "[TRANSLATE: Forgot password?]",
    "loginError": "[TRANSLATE: Invalid username or password]"
  },
  "<module>": {
    "listTitle": "[TRANSLATE: Module title]",
    "noItems": "[TRANSLATE: No items found]"
  }
}
```

---

## 4. Import Order Convention

### 4.1 Backend (NestJS)

```typescript
// 1. NestJS core & common
import { Controller, Get, Post, UseGuards } from '@nestjs/common';
import { ApiTags, ApiBearerAuth } from '@nestjs/swagger';

// 2. Third-party libraries
import { Prisma } from '@prisma/client';

// 3. Project common (guards, decorators, types)
import { JwtAuthGuard } from '../../common/guards/jwt-auth.guard';
import { Roles } from '../../common/decorators/roles.decorator';

// 4. Same module (service, DTOs)
import { FeatureService } from './<module>.service';
import { CreateFeatureDto } from './dto/create-<module>.dto';

// 5. Types (type-only imports)
import type { UserPayload } from '../../common/types';
```

### 4.2 Frontend (Vue)

```typescript
// 1. Vue core
import { ref, computed, onMounted, watch } from 'vue'

// 2. Vue ecosystem (router, i18n, pinia)
import { useRouter, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { storeToRefs } from 'pinia'

// 3. Third-party
import { format } from 'date-fns'

// 4. Project stores
import { useFeatureStore } from '@/stores/<module>'

// 5. Project components
import StatusBadge from '@/components/common/StatusBadge.vue'

// 6. Project services/utils
import { featureService } from '@/services/<module>.service'

// 7. Types (type-only imports)
import type { Feature, QueryParams } from '@/types/<module>'
```

---

## 5. Comment Convention

### 5.1 Section Dividers

```typescript
// ── State ──
const count = ref(0)

// ── Computed ──
const doubled = computed(() => count.value * 2)

// ── Methods ──
function increment(): void {
  count.value++
}

// ── Lifecycle ──
onMounted(() => {
  // ...
})
```

### 5.2 JSDoc (Public API)

```typescript
/**
 * [ACTION] a [entity].
 * [WHAT IT VALIDATES OR DOES]
 *
 * @param id - [Entity] ID
 * @param body - [Description of payload]
 * @param user - Current user from JWT
 * @throws HttpException if [condition]
 */
async process(id: number, body: ActionDto, user: UserPayload): Promise<Feature> {
  // ...
}
```

### 5.3 TODO Convention

```typescript
// TODO(feat): [Description] - Sprint [N]
// TODO(perf): [Description] - before production
// TODO(fix): [Description] - ISSUE-[ID]
// FIXME: [Description of known bug or race condition]
// HACK: Temporary workaround for [reason]
// [CUSTOMIZE: add project-specific comment patterns]
```

---

## 6. Error Message Convention

### 6.1 Backend Error Messages

```typescript
// [CUSTOMIZE: use project language for user-facing errors]
throw new HttpException('[Entity] not found', HttpStatus.NOT_FOUND);
throw new HttpException('Invalid status transition', HttpStatus.BAD_REQUEST);
throw new HttpException('You do not have permission to perform this action', HttpStatus.FORBIDDEN);
throw new HttpException('Invalid username or password', HttpStatus.UNAUTHORIZED);
```

### 6.2 Frontend Error Handling

```typescript
// Store action error handling pattern
async function fetchData(): Promise<void> {
  loading.value = true
  error.value = null
  try {
    const response = await service.getData()
    data.value = response
  } catch (err) {
    if (err instanceof Error) {
      error.value = err.message
    }
    // Show toast notification
    useSnackbar().show(t('common.error'), 'error')
  } finally {
    loading.value = false
  }
}
```

---

## 7. Testing Convention

> Detailed test methodology in `docs/TEST_VIEWPOINT.md`

### 7.1 Test File Location

| Type | Path | Pattern |
|------|------|---------|
| BE Unit | `backend/src/modules/<mod>/<mod>.spec.ts` | Co-located |
| FE Store | `frontend/__tests__/stores/<store>.test.ts` | `__tests__/` |
| FE Component | `frontend/__tests__/components/<Comp>.test.ts` | `__tests__/` |
| FE View | `frontend/__tests__/views/<View>.test.ts` | `__tests__/` |
| FE Integration | `frontend/__tests__/integration/<flow>.test.ts` | `__tests__/` |
| BE E2E | `backend/test/<module>.e2e-spec.ts` | `test/` |

### 7.2 Test Naming Convention

```typescript
describe('[ClassName]Service', () => {               // Class/Module under test
  describe('[methodName]', () => {                   // Method under test
    it('should [expected behavior] when [condition]', ...)  // Happy path
    it('should throw [error] if [condition]', ...)          // Error case
    it('should [enforce rule] for [business rule]', ...)    // Business rule
  })
})
```

---

## Quick Reference: File Naming

```
Backend:                          Frontend:
├── <module>.module.ts            ├── <Module>List.vue     (PascalCase)
├── <module>.controller.ts        ├── StatusBadge.vue      (PascalCase)
├── <module>.service.ts           ├── <module>.service.ts  (kebab-case)
├── create-<module>.dto.ts        ├── <module>.ts          (store, kebab-case)
├── query-<module>.dto.ts         ├── <module>.ts          (type, kebab-case)
├── <module>.entity.ts            ├── use[Feature].ts      (camelCase composable)
└── <module>.spec.ts              └── <module>.test.ts     (kebab-case test)
```
