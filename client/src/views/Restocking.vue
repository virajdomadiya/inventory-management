<template>
  <div class="restocking">
    <div class="page-header">
      <h2>{{ t('restocking.title') }}</h2>
      <p>{{ t('restocking.description') }}</p>
    </div>

    <div v-if="loading" class="loading">{{ t('common.loading') }}</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else>
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">{{ t('restocking.budgetLabel') }}</h3>
        </div>
        <div class="budget-controls">
          <input
            type="range"
            :min="0"
            :max="maxBudget"
            :step="100"
            v-model.number="budget"
            class="budget-slider"
          />
          <div class="budget-readout">{{ currencySymbol }}{{ budget.toLocaleString() }}</div>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <h3 class="card-title">{{ t('restocking.recommendedItems') }}</h3>
        </div>

        <div class="stats-grid">
          <div class="stat-card info">
            <div class="stat-label">{{ t('restocking.stats.itemsRecommended') }}</div>
            <div class="stat-value">{{ recommendations.length }}</div>
          </div>
          <div class="stat-card">
            <div class="stat-label">{{ t('restocking.stats.totalUnits') }}</div>
            <div class="stat-value">{{ totalUnits }}</div>
          </div>
          <div class="stat-card success">
            <div class="stat-label">{{ t('restocking.stats.totalCost') }}</div>
            <div class="stat-value">{{ currencySymbol }}{{ totalCost.toLocaleString() }}</div>
          </div>
          <div class="stat-card warning">
            <div class="stat-label">{{ t('restocking.stats.budgetRemaining') }}</div>
            <div class="stat-value">{{ currencySymbol }}{{ budgetRemaining.toLocaleString() }}</div>
          </div>
        </div>

        <div v-if="recommendations.length === 0" class="no-recommendations">
          {{ t('restocking.noRecommendations') }}
        </div>
        <div v-else class="table-container">
          <table>
            <thead>
              <tr>
                <th>{{ t('restocking.table.sku') }}</th>
                <th>{{ t('restocking.table.itemName') }}</th>
                <th>{{ t('restocking.table.currentDemand') }}</th>
                <th>{{ t('restocking.table.forecastedDemand') }}</th>
                <th>{{ t('restocking.table.gap') }}</th>
                <th>{{ t('restocking.table.unitCost') }}</th>
                <th>{{ t('restocking.table.recommendedQty') }}</th>
                <th>{{ t('restocking.table.lineCost') }}</th>
                <th>{{ t('restocking.table.fill') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in recommendations" :key="item.item_sku">
                <td><strong>{{ item.item_sku }}</strong></td>
                <td>{{ item.item_name }}</td>
                <td>{{ item.current_demand }}</td>
                <td>{{ item.forecasted_demand }}</td>
                <td>{{ item.gap }}</td>
                <td>{{ currencySymbol }}{{ item.unit_cost }}</td>
                <td>{{ item.recommended_quantity }}</td>
                <td>{{ currencySymbol }}{{ item.line_cost.toLocaleString() }}</td>
                <td>
                  <span :class="['badge', item.partial ? 'warning' : 'success']">
                    {{ item.partial ? 'Partial' : 'Full' }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="place-order-row">
          <button
            class="po-button create"
            :disabled="recommendations.length === 0 || submitting"
            @click="submitOrder"
          >
            {{ submitting ? t('restocking.placingOrder') : t('restocking.placeOrder') }}
          </button>
          <p v-if="submitError" class="error">{{ submitError }}</p>
          <p v-if="successMessage" class="badge success success-message">{{ successMessage }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { api } from '../api'
import { useI18n } from '../composables/useI18n'

export default {
  name: 'Restocking',
  setup() {
    const { t, currentCurrency } = useI18n()

    const currencySymbol = computed(() => {
      return currentCurrency.value === 'JPY' ? '¥' : '$'
    })

    const loading = ref(true)
    const error = ref(null)
    const forecasts = ref([])
    const budget = ref(0)
    const submitting = ref(false)
    const submitError = ref(null)
    const successMessage = ref(null)

    const loadForecasts = async () => {
      try {
        loading.value = true
        error.value = null
        forecasts.value = await api.getDemandForecasts()
      } catch (err) {
        error.value = 'Failed to load demand forecasts: ' + err.message
      } finally {
        loading.value = false
      }
    }

    const candidates = computed(() =>
      forecasts.value
        .map(f => ({ ...f, gap: f.forecasted_demand - f.current_demand }))
        .filter(f => f.gap > 0 && f.unit_cost)
        .sort((a, b) => b.gap - a.gap)
    )

    const maxBudget = computed(() => {
      const total = candidates.value.reduce((sum, f) => sum + f.gap * f.unit_cost, 0)
      return Math.ceil(total / 1000) * 1000 || 1000
    })

    const recommendations = computed(() => {
      let remaining = budget.value
      const result = []
      for (const item of candidates.value) {
        if (remaining <= 0) break
        const fullCost = item.gap * item.unit_cost
        if (fullCost <= remaining) {
          result.push({ ...item, recommended_quantity: item.gap, line_cost: fullCost, partial: false })
          remaining -= fullCost
        } else {
          const affordableQty = Math.floor(remaining / item.unit_cost)
          if (affordableQty > 0) {
            result.push({ ...item, recommended_quantity: affordableQty, line_cost: affordableQty * item.unit_cost, partial: true })
          }
          break
        }
      }
      return result
    })

    const totalCost = computed(() => recommendations.value.reduce((s, r) => s + r.line_cost, 0))
    const totalUnits = computed(() => recommendations.value.reduce((s, r) => s + r.recommended_quantity, 0))
    const budgetRemaining = computed(() => budget.value - totalCost.value)

    const submitOrder = async () => {
      submitting.value = true
      submitError.value = null
      successMessage.value = null
      try {
        const payload = {
          budget: budget.value,
          items: recommendations.value.map(r => ({
            item_sku: r.item_sku,
            item_name: r.item_name,
            quantity: r.recommended_quantity,
            unit_cost: r.unit_cost
          }))
        }
        const order = await api.submitRestockOrder(payload)
        successMessage.value = t('restocking.orderSuccess', { orderNumber: order.order_number })
      } catch (err) {
        submitError.value = 'Failed to place restock order: ' + err.message
      } finally {
        submitting.value = false
      }
    }

    onMounted(loadForecasts)

    return {
      t,
      loading,
      error,
      forecasts,
      budget,
      maxBudget,
      recommendations,
      totalCost,
      totalUnits,
      budgetRemaining,
      currencySymbol,
      submitting,
      submitError,
      successMessage,
      submitOrder
    }
  }
}
</script>

<style scoped>
.budget-controls {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.budget-slider {
  flex: 1;
  accent-color: #3b82f6;
}

.budget-readout {
  min-width: 120px;
  text-align: right;
  font-size: 1.25rem;
  font-weight: 700;
  color: #0f172a;
}

.no-recommendations {
  padding: 2rem;
  text-align: center;
  color: #64748b;
  font-size: 0.938rem;
}

.place-order-row {
  margin-top: 1.25rem;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.75rem;
}

.success-message {
  font-size: 0.875rem;
}

.po-button {
  padding: 0.625rem 1.25rem;
  border: none;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.po-button.create {
  background: #3b82f6;
  color: white;
}

.po-button.create:hover:not(:disabled) {
  background: #2563eb;
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(59, 130, 246, 0.3);
}

.po-button.create:disabled {
  background: #cbd5e1;
  cursor: not-allowed;
}
</style>
