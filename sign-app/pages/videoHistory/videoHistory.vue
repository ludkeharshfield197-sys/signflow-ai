<template>
	<view class="video-history-container">
		<!-- 顶部导航栏 -->
		<view class="nav-bar">
			<view class="nav-back" @tap="goBack">
				<uni-icons type="back" size="24" color="#333"></uni-icons>
			</view>
			<view class="nav-title">视频识别历史</view>
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
					<!-- <view class="record-header">
						<text class="time">{{formatTime(item.detection_time)}}</text>
						<text class="model-name">模型: {{item.model.name}}</text>
					</view> -->
					<view class="record-content">
						<video class="preview" :src="item.result_video || item.video_file" controls></video>
						<view class="result" @tap="generateSentence(item)">
							<text class="label">识别结果：</text>
							<text class="value" v-if="item.generatedSentence">{{item.generatedSentence}}</text>
							<text class="value" v-else>{{formatResult(item.detection_result_summary)}} <text class="generate-hint">(点击生成句子)</text></text>
						</view>
						<!-- <view class="params">
							<text class="param-item">IoU阈值: {{item.iou_threshold}}</text>
							<text class="param-item">置信度阈值: {{item.confidence_threshold}}</text>
						</view> -->
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
				
				<!-- 空状态 -->
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
			refreshing: false,
			loading: false,
			page: 1,
			pageSize: 5, // 视频页面降低每页数量
			hasMore: true,
			baseUrl: getServerUrl(),
			generateLoading: false // 新增：表示是否正在生成句子
		}
	},
	onLoad() {
		// 加载数据
		this.loadRecords();
	},
	methods: {
		// 返回上一页
		goBack() {
			uni.navigateBack();
		},
		
		// 格式化时间
		formatTime(timestamp) {
			if(!timestamp) return '';
			return timestamp.replace('T', ' ').split('.')[0];
		},
		
		// 格式化识别结果
		formatResult(summary) {
			if(!summary || Object.keys(summary).length === 0) return '无识别结果';
			
			return Object.entries(summary)
				.map(([key, value]) => `${key}(${value})`)
				.join('、');
		},
		
		// 加载记录
		async loadRecords() {
			if(this.loading) return;
			
			this.loading = true;
			console.log('开始加载视频记录，页码:', this.page);
			
			try {
				// 使用封装的request方法
				const res = await request.get('video/list/', {
					page: this.page,
					pageSize: this.pageSize
				});
				
				console.log('加载视频记录响应:', res);
				
				if(res.code === 200) {
					const newRecords = res.data.list || [];
					
					if(this.page === 1) {
						this.records = newRecords;
					} else {
						this.records = [...this.records, ...newRecords];
					}
					
					this.hasMore = this.records.length < res.data.total;
					console.log('加载视频记录成功，总数:', res.data.total, '当前记录数:', this.records.length);
				} else {
					uni.showToast({
						title: res.message || '加载失败',
						icon: 'none'
					});
				}
			} catch(e) {
				console.error('加载视频记录失败:', e);
				uni.showToast({
					title: '网络错误',
					icon: 'none'
				});
			} finally {
				this.loading = false;
				this.refreshing = false;
			}
		},
		
		// 处理删除
		handleDelete(id) {
			uni.showModal({
				title: '提示',
				content: '确定要删除这条记录吗？',
				success: (res) => {
					if(res.confirm) {
						this.deleteRecord(id);
					}
				}
			});
		},
		
		// 执行删除
		async deleteRecord(id) {
			console.log(`准备删除视频记录ID: ${id}`);
			
			try {
				// 与图片删除保持一致的方式
				const res = await request.post('video/delete/', {
					ids: [id]  // 注意这里需要传递一个数组
				});
				
				console.log('删除视频响应:', res);
				
				if(res.code === 200) {
					uni.showToast({
						title: '删除成功',
						icon: 'success'
					});
					
					// 从列表中移除
					this.records = this.records.filter(item => item.id !== id);
					
					// 如果删除后记录不足，加载更多
					if(this.records.length < this.pageSize && this.hasMore) {
						this.loadMore();
					}
				} else {
					uni.showToast({
						title: res.message || '删除失败',
						icon: 'none'
					});
				}
			} catch(err) {
				console.error('删除视频请求失败:', err);
				uni.showToast({
					title: '删除失败，网络错误',
					icon: 'none'
				});
			}
		},
		
		// 下拉刷新
		refresh() {
			this.page = 1;
			this.refreshing = true;
			this.hasMore = true;
			this.loadRecords();
		},
		
		// 上拉加载更多
		loadMore() {
			if(!this.hasMore || this.loading) return;
			this.page++;
			this.loadRecords();
		},
		
		// 点击识别结果，生成句子
		async generateSentence(item) {
			// 如果已经生成过句子，不重复生成
			if (item.generatedSentence) {
				return;
			}
			
			// 如果正在生成中，不重复请求
			if (this.generateLoading) {
				uni.showToast({
					title: '正在生成中，请稍候',
					icon: 'none'
				});
				return;
			}
			
			// 显示加载状态
			this.generateLoading = true;
			uni.showLoading({
				title: '生成句子中...',
				mask: true
			});
			
			try {
				// 调用API生成句子，使用视频ID
				const res = await request.get(`video/sentence/?task_id=${item.id}`);
				console.log('生成句子响应:', res);
				
				if (res.code === 200 && res.data && res.data.sentence) {
					// 成功获取句子，更新显示
					this.$set(item, 'generatedSentence', res.data.sentence);
					uni.showToast({
						title: '句子生成成功',
						icon: 'success'
					});
				} else if (res.code === 400 && res.message && 
						 (res.message.includes('正在处理') || res.message.includes('尚未处理完成'))) {
					// 处理中，显示提示
					uni.showToast({
						title: '句子正在生成中，请稍后再试',
						icon: 'none',
						duration: 2000
					});
				} else {
					// 生成失败
					uni.showToast({
						title: res.message || '生成句子失败',
						icon: 'none'
					});
				}
			} catch (error) {
				console.error('生成句子请求失败:', error);
				uni.showToast({
					title: '网络请求失败',
					icon: 'none'
				});
			} finally {
				// 无论成功失败，都关闭加载提示
				this.generateLoading = false;
				uni.hideLoading();
			}
		}
	}
}
</script>

<style>
.video-history-container {
	display: flex;
	flex-direction: column;
	min-height: 100vh;
	background-color: #f5f5f5;
}

.nav-bar {
	display: flex;
	align-items: center;
	height: 90rpx;
	background-color: #fff;
	border-bottom: 1rpx solid #eee;
	position: relative;
}

.nav-back {
	width: 90rpx;
	height: 90rpx;
	display: flex;
	justify-content: center;
	align-items: center;
}

.nav-title {
	position: absolute;
	left: 0;
	right: 0;
	text-align: center;
	font-size: 32rpx;
	font-weight: bold;
	color: #333;
}

.scroll-view {
	flex: 1;
}

.record-list {
	padding: 20rpx;
}

.record-item {
	background-color: #fff;
	border-radius: 12rpx;
	margin-bottom: 20rpx;
	box-shadow: 0 2rpx 10rpx rgba(0, 0, 0, 0.05);
	overflow: hidden;
}

.record-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	padding: 20rpx;
	border-bottom: 1rpx solid #eee;
}

.time {
	font-size: 24rpx;
	color: #999;
}

.model-name {
	font-size: 24rpx;
	color: #1890ff;
	background-color: rgba(24, 144, 255, 0.1);
	padding: 4rpx 12rpx;
	border-radius: 20rpx;
}

.record-content {
	padding: 20rpx;
}

.preview {
	width: 100%;
	height: 400rpx;
	border-radius: 8rpx;
	margin-bottom: 20rpx;
}

.result {
	display: flex;
	flex-wrap: wrap;
	margin-bottom: 16rpx;
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

.generate-hint {
	font-size: 24rpx;
	color: #1890ff;
	margin-left: 10rpx;
}

.params {
	display: flex;
	flex-wrap: wrap;
	margin-bottom: 16rpx;
}

.param-item {
	font-size: 24rpx;
	color: #666;
	margin-right: 20rpx;
	margin-bottom: 8rpx;
}

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
	font-size: 24rpx;
	font-style: normal;
	-webkit-font-smoothing: antialiased;
	-moz-osx-font-smoothing: grayscale;
}

.icon-back:before {
	content: "\e7ed";
	font-size: 36rpx;
}

.icon-delete:before {
	content: "\e6e2";
	font-family: "iconfont";
	font-size: 28rpx;
}
</style> 