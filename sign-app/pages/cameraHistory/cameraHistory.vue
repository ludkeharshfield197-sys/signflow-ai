<template>
	<view class="camera-history-container">
		<!-- 顶部导航栏 -->
		<view class="nav-bar">
			<view class="nav-back" @tap="goBack">
				<uni-icons type="back" size="24" color="#333"></uni-icons>
			</view>
			<view class="nav-title">摄像头识别历史</view>
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
						<text class="time">{{formatTime(item.start_time)}}</text>
						<text class="status" :class="getStatusClass(item)">{{getStatusText(item)}}</text>
					</view>
					<view class="record-content">

						<view class="detail-row">
							<text class="label">会话时长：</text>
							<text class="value">{{calculateDuration(item.start_time, item.end_time)}}</text>
						</view>
						<view class="detail-row">
							<text class="label">识别次数：</text>
							<text class="value">{{item.detection_count || 0}}</text>
						</view>
						<view class="result">
							<text class="label">{{item.generatedSentence ? '生成句子：' : '结果摘要：'}}</text>
							<text class="value">
								<text v-if="item.generatedSentence">{{item.generatedSentence}}</text>
								<text v-else>{{formatSummary(item.detection_summary)}}</text>
							</text>
						</view>
					</view>
					<view class="record-footer">
						<view class="action-btn generate-sentence" @tap="generateSentence(item)" v-if="!item.generatedSentence">
							<uni-icons type="compose" size="16" color="#1890ff"></uni-icons>
							<text>生成句子</text>
						</view>
						<view class="action-btn sentence-result" @tap="showSentence(item)" v-else>
							<uni-icons type="file-text" size="16" color="#52c41a"></uni-icons>
							<text>查看句子</text>
						</view>
						<view class="action-btn delete" @tap="deleteRecord(item)">
							<uni-icons type="trash" size="16" color="#ff4d4f"></uni-icons>
							<text>删除</text>
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
		
		<!-- 句子结果弹窗 -->
		<uni-popup ref="sentencePopup" type="center">
			<view class="detail-popup">
				<view class="popup-header">
					<text class="popup-title">句子结果</text>
					<view class="popup-close" @tap="closeSentencePopup">
						<uni-icons type="close" size="18" color="#999"></uni-icons>
					</view>
				</view>
				<view class="popup-content">
					<view class="sentence-content">
						<text selectable>{{currentSentence}}</text>
					</view>
				</view>
				<view class="popup-footer">
					<button class="popup-btn" type="default" @tap="closeSentencePopup">关闭</button>
					<button class="popup-btn" type="primary" @tap="copySentence">复制</button>
				</view>
			</view>
		</uni-popup>
	</view>
</template>

<script>
import request from '../../utils/request.js';

export default {
	data() {
		return {
			records: [],
			refreshing: false,
			loading: false,
			pageNum: 1,
			pageSize: 10,
			hasMore: true,
			generateLoading: false, // 是否正在生成句子
			currentSentence: null // 当前显示的句子
		}
	},
	onLoad() {
		// 检查登录状态
		this.checkLoginStatus();
		// 加载数据
		this.loadRecords();
	},
	methods: {
		// 检查登录状态
		checkLoginStatus() {
			const token = uni.getStorageSync('token');
			const userInfoStr = uni.getStorageSync('currentUser');
			
			if (!token || !userInfoStr) {
				uni.showToast({
					title: '请先登录',
					icon: 'none'
				});
				setTimeout(() => {
					uni.navigateTo({
						url: '/pages/login/login?redirect=/pages/cameraHistory/cameraHistory'
					});
				}, 1500);
				return;
			}
		},
		
		// 返回上一页
		goBack() {
			uni.navigateBack();
		},
		
		// 加载记录
		async loadRecords(isRefresh = false) {
			if (this.loading) return;
			
			this.loading = true;
			const pageNum = isRefresh ? 1 : this.pageNum;
			
			try {
				const res = await request.get('camera/sessions/', {
					params: {
						page: pageNum,
						pageSize: this.pageSize
					}
				});
				
				if (res.code === 200) {
					const data = res.data.list || [];
					
					if (isRefresh) {
						this.records = data;
						this.pageNum = 1;
					} else {
						this.records = [...this.records, ...data];
						this.pageNum++;
					}
					
					// 判断是否还有更多数据
					this.hasMore = data.length === this.pageSize;
				} else {
					uni.showToast({
						title: res.message || '获取记录失败',
						icon: 'none'
					});
				}
			} catch (error) {
				console.error('获取记录失败:', error);
				uni.showToast({
					title: '网络请求失败',
					icon: 'none'
				});
			} finally {
				this.loading = false;
				if (isRefresh) {
					this.refreshing = false;
					uni.stopPullDownRefresh();
				}
			}
		},
		
		// 下拉刷新
		refresh() {
			this.refreshing = true;
			this.loadRecords(true);
		},
		
		// 加载更多
		loadMore() {
			if (!this.hasMore || this.loading) return;
			this.loadRecords();
		},
		
		// 生成句子
		async generateSentence(item) {
			// 如果已经在生成中，不重复请求
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
				// 调用API生成句子，使用会话ID
				const res = await request.get(`camera/sentence/?session_id=${item.session_id}`);
				console.log('生成句子响应:', res);
				
				if (res.code === 200 && res.data && res.data.sentence) {
					// 成功获取句子，更新显示
					this.$set(item, 'generatedSentence', res.data.sentence);
					
					// 不再自动打开弹窗，而是直接在列表中显示句子
					this.currentSentence = res.data.sentence;
					
					uni.showToast({
						title: '句子生成成功',
						icon: 'success'
					});
				} else if (res.code === 400 && res.message && 
						(res.message.includes('正在处理') || 
						 res.message.includes('尚未处理完成') || 
						 res.message.includes('未找到'))) {
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
		},
		
		// 查看已生成的句子
		showSentence(item) {
			if (item.generatedSentence) {
				this.currentSentence = item.generatedSentence;
				this.$refs.sentencePopup.open();
			} else {
				uni.showToast({
					title: '尚未生成句子',
					icon: 'none'
				});
			}
		},
		
		// 关闭句子弹窗
		closeSentencePopup() {
			this.$refs.sentencePopup.close();
		},
		
		// 复制句子
		copySentence() {
			if (this.currentSentence) {
				uni.setClipboardData({
					data: this.currentSentence,
					success: () => {
						uni.showToast({
							title: '已复制到剪贴板',
							icon: 'success'
						});
					}
				});
			}
		},
		
		// 删除记录
		deleteRecord(item) {
			uni.showModal({
				title: '确认删除',
				content: '确定要删除这条记录吗？',
				success: async (res) => {
					if (res.confirm) {
						try {
							uni.showLoading({
								title: '删除中...',
								mask: true
							});
							
							const response = await request.post('camera/sessions/', {
								ids: [item.id]
							});
							
							if (response.code === 200) {
								uni.showToast({
									title: '删除成功',
									icon: 'success'
								});
								
								// 刷新列表
								this.refresh();
							} else {
								uni.showToast({
									title: response.message || '删除失败',
									icon: 'none'
								});
							}
						} catch (error) {
							console.error('删除失败:', error);
							uni.showToast({
								title: '网络请求失败',
								icon: 'none'
							});
						} finally {
							uni.hideLoading();
						}
					}
				}
			});
		},
		
		// 格式化时间
		formatTime(timeStr) {
			if (!timeStr) return '未知时间';
			
			try {
				// 将后端返回的格式转换为iOS支持的格式
				const formattedTimeStr = timeStr.replace(' ', 'T');
				const date = new Date(formattedTimeStr);
				
				// 检查日期是否有效
				if (isNaN(date.getTime())) {
					console.error('无效的日期格式:', timeStr);
					return '日期格式错误';
				}
				
				// 格式化输出
				const year = date.getFullYear();
				const month = String(date.getMonth() + 1).padStart(2, '0');
				const day = String(date.getDate()).padStart(2, '0');
				const hours = String(date.getHours()).padStart(2, '0');
				const minutes = String(date.getMinutes()).padStart(2, '0');
				const seconds = String(date.getSeconds()).padStart(2, '0');
				
				return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
			} catch (e) {
				console.error('日期格式化错误:', e);
				return '时间格式化错误';
			}
		},
		
		// 计算会话时长
		calculateDuration(startTime, endTime) {
			if (!startTime || !endTime) return '未完成';
			
			try {
				// 将后端返回的格式转换为iOS支持的格式
				const formattedStartTime = startTime.replace(' ', 'T');
				const formattedEndTime = endTime.replace(' ', 'T');
				
				const start = new Date(formattedStartTime).getTime();
				const end = new Date(formattedEndTime).getTime();
				
				if (isNaN(start) || isNaN(end)) {
					console.error('无效的日期格式:', startTime, endTime);
					return '时长计算错误';
				}
				
				const diff = Math.floor((end - start) / 1000); // 秒
				
				if (diff < 60) {
					return `${diff}秒`;
				} else if (diff < 3600) {
					const minutes = Math.floor(diff / 60);
					const seconds = diff % 60;
					return `${minutes}分${seconds}秒`;
				} else {
					const hours = Math.floor(diff / 3600);
					const minutes = Math.floor((diff % 3600) / 60);
					return `${hours}小时${minutes}分`;
				}
			} catch (e) {
				console.error('时长计算错误:', e);
				return '计算错误';
			}
		},
		
		// 获取状态文本
		getStatusText(item) {
			if (!item.end_time) return '进行中';
			return item.detection_count > 0 ? '已完成' : '无结果';
		},
		
		// 获取状态样式类
		getStatusClass(item) {
			if (!item.end_time) return 'pending';
			return item.detection_count > 0 ? 'success' : 'failed';
		},
		
		// 格式化摘要
		formatSummary(summary) {
			if (!summary || Object.keys(summary).length === 0) {
				return '无识别结果';
			}
			
			return Object.entries(summary)
				.map(([key, value]) => `${key}(${value})`)
				.join('、');
		}
	}
}
</script>

<style>
.camera-history-container {
	background-color: #f5f7fa;
	min-height: 100vh;
}

.nav-bar {
	display: flex;
	align-items: center;
	height: 90rpx;
	background-color: #fff;
	padding: 0 30rpx;
	box-shadow: 0 2rpx 10rpx rgba(0, 0, 0, 0.05);
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
	height: calc(100vh - 90rpx);
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

.detail-row {
	display: flex;
	margin-bottom: 10rpx;
}

.result {
	display: flex;
	flex-wrap: wrap;
	margin-top: 10rpx;
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

.record-footer {
	display: flex;
	padding: 20rpx;
	border-top: 1rpx solid #eee;
	justify-content: space-between;
}

.action-btn {
	display: flex;
	align-items: center;
	padding: 10rpx 20rpx;
	border-radius: 30rpx;
	font-size: 24rpx;
	margin-left: 10rpx;
}

.action-btn text {
	margin-left: 6rpx;
}

.action-btn.view-detail {
	background-color: rgba(54, 207, 201, 0.1);
	color: #36cfc9;
	border: 1rpx solid #87e8de;
}

.action-btn.generate-sentence {
	background-color: rgba(24, 144, 255, 0.1);
	color: #1890ff;
	border: 1rpx solid #91d5ff;
}

.action-btn.sentence-result {
	background-color: rgba(82, 196, 26, 0.1);
	color: #52c41a;
	border: 1rpx solid #b7eb8f;
}

.action-btn.delete {
	background-color: #fff1f0;
	color: #ff4d4f;
	border: 1rpx solid #ffa39e;
}

.popup-close {
	width: 60rpx;
	height: 60rpx;
	display: flex;
	justify-content: center;
	align-items: center;
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

/* 弹窗基本样式 */
.detail-popup {
	background-color: #fff;
	border-radius: 12rpx;
	width: 650rpx;
	max-height: 80vh;
	display: flex;
	flex-direction: column;
}

.popup-header {
	padding: 30rpx;
	border-bottom: 1rpx solid #eee;
	display: flex;
	justify-content: space-between;
	align-items: center;
}

.popup-title {
	font-size: 32rpx;
	font-weight: bold;
	color: #333;
}

.popup-content {
	padding: 30rpx;
	max-height: 60vh;
}

.popup-footer {
	padding: 20rpx 30rpx;
	border-top: 1rpx solid #eee;
	display: flex;
	justify-content: space-between;
}

.popup-btn {
	width: 45%;
	font-size: 28rpx;
	margin: 0;
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

.icon-generate:before {
	content: "\e74d";
}

.icon-text:before {
	content: "\e791";
}

.sentence-content {
	background-color: #f8f8f8;
	padding: 20rpx;
	border-radius: 8rpx;
	font-size: 28rpx;
	color: #333;
	line-height: 1.6;
	word-break: break-all;
	max-height: 300rpx;
	overflow-y: auto;
}
</style> 