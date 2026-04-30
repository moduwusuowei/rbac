<template>
  <div class="customer-products">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1>商品浏览</h1>
      <p>浏览我们的全部商品</p>
    </div>
    
    <!-- 搜索和筛选区 -->
    <div class="filter-section">
      <div class="search-box">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索商品..."
          prefix-icon="Search"
          @keyup.enter="handleSearch"
        >
          <template #append>
            <el-button @click="handleSearch"><el-icon><Search /></el-icon></el-button>
          </template>
        </el-input>
      </div>
      
      <div class="filter-controls">
        <el-select v-model="sortBy" placeholder="排序方式" @change="handleSort">
          <el-option label="价格从低到高" value="price_asc" />
          <el-option label="价格从高到低" value="price_desc" />
          <el-option label="上架时间从新到旧" value="created_new" />
          <el-option label="上架时间从旧到新" value="created_old" />
        </el-select>
        
        <el-button-group>
          <el-button 
            :type="viewMode === 'grid' ? 'primary' : 'default'"
            @click="viewMode = 'grid'"
          >
            <el-icon><Grid /></el-icon>
            网格
          </el-button>
          <el-button 
            :type="viewMode === 'list' ? 'primary' : 'default'"
            @click="viewMode = 'list'"
          >
            <el-icon><List /></el-icon>
            列表
          </el-button>
        </el-button-group>
      </div>
    </div>
    
    <!-- 商品列表 -->
    <div class="products-container" :class="viewMode">
      <div 
        v-for="product in filteredProducts" 
        :key="product.id"
        class="product-card"
      >
        <div class="product-image">
          <img 
            :src="product.image_url || `https://picsum.photos/seed/${product.id}/400/300`" 
            :alt="product.name"
            loading="lazy"
          />
          <div v-if="!product.is_active" class="product-status">已下架</div>
        </div>
        
        <div class="product-info">
          <h3 class="product-name">{{ product.name }}</h3>
          <p class="product-description">{{ product.description || '暂无描述' }}</p>
          <div class="product-price">¥{{ product.price.toFixed(2) }}</div>
          <div class="product-stock">
            <span :class="product.stock > 0 ? 'in-stock' : 'out-of-stock'">
              {{ product.stock > 0 ? '有货' : '缺货' }}
            </span>
            <span class="stock-count">库存: {{ product.stock }}</span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 空状态 -->
    <div v-if="filteredProducts.length === 0" class="empty-state">
      <el-empty description="暂无商品" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Search, Grid, List } from '@element-plus/icons-vue'
import apiClient from '@/utils/request'

// 状态
const products = ref([])
const searchKeyword = ref('')
const sortBy = ref('')
const viewMode = ref('grid')

// 计算属性：过滤和排序后的商品
const filteredProducts = computed(() => {
  let result = [...products.value]
  
  // 搜索过滤
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    result = result.filter(product => 
      product.name.toLowerCase().includes(keyword) ||
      product.description?.toLowerCase().includes(keyword) ||
      product.code.toLowerCase().includes(keyword)
    )
  }
  
  // 排序
  switch (sortBy.value) {
    case 'price_asc':
      result.sort((a, b) => a.price - b.price)
      break
    case 'price_desc':
      result.sort((a, b) => b.price - a.price)
      break
    case 'created_new':
      result.sort((a, b) => {
        const dateA = a.created_at ? new Date(a.created_at) : new Date(0)
        const dateB = b.created_at ? new Date(b.created_at) : new Date(0)
        return dateB - dateA
      })
      break
    case 'created_old':
      result.sort((a, b) => {
        const dateA = a.created_at ? new Date(a.created_at) : new Date(0)
        const dateB = b.created_at ? new Date(b.created_at) : new Date(0)
        return dateA - dateB
      })
      break
  }
  
  return result
})

// 获取商品列表
const fetchProducts = async () => {
  try {
    // 直接使用相对路径，baseURL已经包含/api/v1
    const response = await apiClient.get('/public/products')
    products.value = response.data
  } catch (error) {
    console.error('获取商品列表失败', error)
    console.error('错误详情:', error.response?.data)
  }
}

// 搜索
const handleSearch = () => {
  // 搜索逻辑已在计算属性中处理
}

// 排序
const handleSort = () => {
  // 排序逻辑已在计算属性中处理
}

onMounted(() => {
  fetchProducts()
})
</script>

<style scoped>
.customer-products {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  text-align: center;
  margin-bottom: 40px;
}

.page-header h1 {
  font-size: 32px;
  font-weight: 700;
  color: #303133;
  margin-bottom: 10px;
}

.page-header p {
  font-size: 16px;
  color: #606266;
}

.filter-section {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  margin-bottom: 30px;
  align-items: center;
}

.search-box {
  flex: 1;
  min-width: 300px;
}

.search-box .el-input {
  width: 100%;
}

.filter-controls {
  display: flex;
  gap: 10px;
  align-items: center;
  flex-direction: row;
}

.el-button-group {
  display: flex;
  flex-direction: row;
}

.el-button-group .el-button {
  margin: 0;
  border-radius: 0;
}

.el-button-group .el-button:first-child {
  border-top-left-radius: 4px;
  border-bottom-left-radius: 4px;
}

.el-button-group .el-button:last-child {
  border-top-right-radius: 4px;
  border-bottom-right-radius: 4px;
}

.products-container {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
}

.products-container.grid {
  justify-content: flex-start;
}

.products-container.list {
  flex-direction: column;
}

.product-card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  overflow: hidden;
  transition: all 0.3s ease;
}

.products-container.grid .product-card {
  width: calc(25% - 15px);
  min-width: 200px;
}

.products-container.list .product-card {
  width: 100%;
  display: flex;
}

.product-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 16px 0 rgba(0, 0, 0, 0.15);
}

.product-image {
  position: relative;
  overflow: hidden;
}

.products-container.grid .product-image {
  height: 200px;
}

.products-container.list .product-image {
  width: 200px;
  height: 150px;
  flex-shrink: 0;
}

.product-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.product-card:hover .product-image img {
  transform: scale(1.05);
}

.product-status {
  position: absolute;
  top: 10px;
  right: 10px;
  background: rgba(0, 0, 0, 0.7);
  color: #fff;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.product-info {
  padding: 16px;
}

.products-container.list .product-info {
  flex: 1;
  padding: 20px;
}

.product-name {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 8px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.products-container.list .product-name {
  font-size: 18px;
  white-space: normal;
  line-height: 1.4;
}

.product-description {
  font-size: 14px;
  color: #606266;
  margin-bottom: 12px;
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.products-container.list .product-description {
  -webkit-line-clamp: 3;
  margin-bottom: 16px;
}

.product-price {
  font-size: 18px;
  font-weight: 700;
  color: #f56c6c;
  margin-bottom: 8px;
}

.product-stock {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 12px;
}

.in-stock {
  color: #67c23a;
}

.out-of-stock {
  color: #f56c6c;
}

.stock-count {
  color: #909399;
}

.empty-state {
  text-align: center;
  padding: 60px 0;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .products-container.grid .product-card {
    width: calc(33.333% - 13.333px);
  }
}

@media (max-width: 768px) {
  .products-container.grid .product-card {
    width: calc(50% - 10px);
  }
  
  .filter-section {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-box {
    min-width: unset;
  }
  
  .filter-controls {
    justify-content: space-between;
  }
  
  .products-container.list .product-card {
    flex-direction: column;
  }
  
  .products-container.list .product-image {
    width: 100%;
    height: 200px;
  }
}

@media (max-width: 480px) {
  .products-container.grid .product-card {
    width: 100%;
  }
  
  .page-header h1 {
    font-size: 24px;
  }
  
  .customer-products {
    padding: 10px;
  }
}
</style>
