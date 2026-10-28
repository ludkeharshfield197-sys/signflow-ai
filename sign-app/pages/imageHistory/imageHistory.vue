<template>
	<view class="image-history-container">
		<!-- 顶部导航栏 -->
		<view class="nav-bar">
			<view class="nav-back" @tap="goBack">
				<uni-icons type="back" size="24" color="#333"></uni-icons>
			</view>
			<view class="nav-title">图片识别历史</view>
		</view>
		
		<!-- 内容区域 -->
		<scroll-view 
			class="scroll-view"
			scroll-y
			@scrolltolower="loadMore"
			@refresherrefresh="refresh"
			:refresher-enabled="true"
			:refresher-triggered="refreshing"
		>
			<view class="record-list">
				<view class="record-item" v-for="(item, index) in records" :key="index">
					<view class="record-header">
						<text class="time">{{formatTime(item.upload_time)}}</text>
						<text class="status" :class="getStatusClass(item.status)">
							{{getStatusText(item.status)}}
						</text>
					</view>
					<view class="record-content">
						<image class="preview" :src="item.result_image || item.image" mode="aspectFill" @tap="previewImage(item)"></image>
						<view class="result">
							<text class="label">识别结果：</text>
							<text class="value">{{formatResult(item.result)}}</text>
						</view>
						<view class="actions">
							<view class="action-btn delete" @tap="handleDelete(item.id)">
								<uni-icons type="trash" size="16" color="#ff4d4f"></uni-icons>
								<text>删除</text>
							</view>
						</view>
					</view>
				</view>
				
				<!-- 加载更多 -->
				<view class="load-more" v-if="records.length > 0 && hasMore">
					<text>加载中...</text>
				</view>
				
				<!-- 没有更多数据 -->
				<view class="no-more" v-if="records.length > 0 && !hasMore">
					<text>没有更多数据了</text>
				</view>
				
				<!-- 暂无数据 -->
				<view class="empty" v-if="records.length === 0 && !loading">
					<image src="/static/empty.png" mode="aspectFit"></image>
					<text>暂无识别记录</text>
				</view>
			</view>
		</scroll-view>
	</view>
</template>

<script>
import request from '../../utils/request.js';
import { getServerUrl } from '../../utils/request.js';

export default {
	data() {
		return {
			records: [],
			page: 1,
			pageSize: 10,
			hasMore: true,
			refreshing: false,
			loading: false,
			baseUrl: getServerUrl()
		}
	},
	
	onLoad() {
		this.loadRecords()
	},
	
	methods: {
		// 返回上一页
		goBack() {
			uni.navigateBack()
		},
		
		// 获取状态样式类
		getStatusClass(status) {
			const statusMap = {
				'completed': 'success',
				'processing': 'pending',
				'failed': 'failed'
			}
			return statusMap[status] || 'pending'
		},
		
		// 获取状态文本
		getStatusText(status) {
			const statusMap = {
				'completed': '识别成功',
				'processing': '处理中',
				'failed': '识别失败'
			}
			return statusMap[status] || '未知状态'
		},
		
		// 格式化时间
		formatTime(timestamp) {
			if(!timestamp) return ''
			return timestamp.replace('T', ' ').split('.')[0]
		},
		
		// 格式化识别结果
		formatResult(result) {
			if(!result || !Array.isArray(result)) return '无识别结果'
			return result.map(item => `${item.class}(${(item.confidence * 100).toFixed(1)}%)`).join('、')
		},
		
		// 预览图片
		previewImage(item) {
			const url = item.result_image || item.image
			uni.previewImage({
				urls: [url],
				current: url
			})
		},
		
		// 加载记录
		async loadRecords() {
			if(this.loading) return
			
			this.loading = true
			console.log('开始加载记录，页码:', this.page)
			
			try {
				// 使用封装的request方法
				const res = await request.get('image/list/', {
					page: this.page,
					pageSize: this.pageSize
				})
				
				console.log('加载记录响应:', res)
				
				if(res.code === 200) {
					const newRecords = res.data.list || []
					
					if(this.page === 1) {
						this.records = newRecords
					} else {
						this.records = [...this.records, ...newRecords]
					}
					
					this.hasMore = this.records.length < res.data.total
					console.log('加载记录成功，总数:', res.data.total, '当前记录数:', this.records.length)
				} else {
					uni.showToast({
						title: res.message || '加载失败',
						icon: 'none'
					})
				}
			} catch(e) {
				console.error('加载记录失败:', e)
				uni.showToast({
					title: '网络错误',
					icon: 'none'
				})
			} finally {
				this.loading = false
				this.refreshing = false
			}
		},
		
		// 处理删除
		handleDelete(id) {
			uni.showModal({
				title: '提示',
				content: '确定要删除这条记录吗？',
				success: (res) => {
					if(res.confirm) {
						this.deleteRecord(id)
					}
				}
			})
		},
		
		// 执行删除
		async deleteRecord(id) {
			console.log(`准备删除记录ID: ${id}`)
			
			try {
				// 修改为与PC端一致的删除方式
				const res = await request.post('image/delete/', {
					ids: [id]  // 注意这里需要传递一个数组
				})
				
				console.log('删除响应:', res)
				
				if(res.code === 200) {
					uni.showToast({
						title: '删除成功',
						icon: 'success'
					})
					
					// 从列表中移除
					this.records = this.records.filter(item => item.id !== id)
					
					// 如果删除后记录不足，加载更多
					if(this.records.length < this.pageSize && this.hasMore) {
						this.loadMore()
					}
				} else {
					uni.showToast({
						title: res.message || '删除失败',
						icon: 'none'
					})
				}
			} catch(err) {
				console.error('删除请求失败:', err)
				uni.showToast({
					title: '删除失败，网络错误',
					icon: 'none'
				})
			}
		},
		
		// 刷新
		refresh() {
			this.page = 1
			this.refreshing = true
			this.hasMore = true
			this.loadRecords()
		},
		
		// 加载更多
		loadMore() {
			if(!this.hasMore || this.loading) return
			this.page++
			this.loadRecords()
		}
	}
}
</script>

<style>
.image-history-container {
	display: flex;
	flex-direction: column;
	height: 100vh;
	background-color: #f5f5f5;
}

.nav-bar {
	display: flex;
	align-items: center;
	height: 90rpx;
	background-color: #ffffff;
	padding: 0 30rpx;
	box-shadow: 0 2rpx 10rpx rgba(0, 0, 0, 0.05);
	position: relative;
	z-index: 10;
}

.nav-back {
	width: 60rpx;
	height: 60rpx;
	display: flex;
	align-items: center;
	justify-content: center;
}

.nav-title {
	flex: 1;
	text-align: center;
	font-size: 32rpx;
	font-weight: bold;
	color: #333;
}

.scroll-view {
	flex: 1;
	width: 100%;
}

.record-list {
	padding: 20rpx;
}

.record-item {
	background-color: #fff;
	border-radius: 12rpx;
	margin-bottom: 20rpx;
	padding: 20rpx;
	box-shadow: 0 2rpx 10rpx rgba(0, 0, 0, 0.05);
}

.record-header {
	display: flex;
	justify-content: space-between;
	margin-bottom: 20rpx;
	border-bottom: 1rpx solid #f0f0f0;
	padding-bottom: 15rpx;
}

.time {
	font-size: 24rpx;
	color: #999;
}

.status {
	font-size: 24rpx;
	padding: 4rpx 12rpx;
	border-radius: 20rpx;
}

.status.success {
	color: #52c41a;
	background-color: rgba(82, 196, 26, 0.1);
}

.status.pending {
	color: #1890ff;
	background-color: rgba(24, 144, 255, 0.1);
}

.status.failed {
	color: #f5222d;
	background-color: rgba(245, 34, 45, 0.1);
}

.record-content {
	padding: 20rpx;
}

.preview {
	width: 100%;
	height: 300rpx;
	border-radius: 8rpx;
	margin-bottom: 20rpx;
}

.result {
	display: flex;
	flex-wrap: wrap;
}

.label {
	font-size: 28rpx;
	color: #666;
	margin-right: 10rpx;
}

.value {
	font-size: 28rpx;
	color: #333;
	flex: 1;
}

.load-more, .no-more {
	text-align: center;
	padding: 20rpx 0;
	font-size: 24rpx;
	color: #999;
}

.empty {
	display: flex;
	flex-direction: column;
	align-items: center;
	padding: 100rpx 0;
}

.empty image {
	width: 200rpx;
	height: 200rpx;
	margin-bottom: 20rpx;
}

.empty text {
	font-size: 28rpx;
	color: #999;
}

/* 图标字体 */
@font-face {
	font-family: 'iconfont';
	src: url('https://at.alicdn.com/t/font_3094026_8g5xcl0xkor.ttf?t=1640767010404') format('truetype');
}

.iconfont {
	font-family: "iconfont" !important;
	font-size: 36rpx;
	font-style: normal;
	-webkit-font-smoothing: antialiased;
	-moz-osx-font-smoothing: grayscale;
}

.icon-back:before {
	content: "\e7ed";
}

/* 添加删除按钮样式 */
.actions {
	display: flex;
	justify-content: flex-end;
	margin-top: 20rpx;
}

.action-btn {
	display: flex;
	align-items: center;
	padding: 10rpx 20rpx;
	border-radius: 30rpx;
	font-size: 24rpx;
}

.action-btn.delete {
	background-color: #fff1f0;
	color: #ff4d4f;
	border: 1rpx solid #ffa39e;
}

.action-btn text {
	margin-left: 6rpx;
}

/* 添加删除图标 */
.icon-delete:before {
	content: "\e6e2";
	font-family: "iconfont";
	font-size: 28rpx;
}
</style> 