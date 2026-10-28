<template>
	<view class="home-container">
		<!-- 欢迎区域 -->
		<view class="welcome-section">
			<view class="welcome-content">
				<image class="logo" src="/static/logo.png" mode="aspectFit"></image>
				<text class="title">手语识别系统</text>
				<text class="subtitle">基于YOLO的智能手语识别与翻译平台</text>
			</view>
		</view>
		
		<!-- 功能卡片区域 -->
		<view class="content-section">
			<view class="section-title">功能选择</view>
			<view class="feature-cards">
				<view 
					class="feature-card" 
					v-for="(feature, index) in features" 
					:key="index" 
					@tap="navigateTo(feature.path)"
				>
					<view class="card-content">
						<view class="feature-icon">
							<image :src="feature.icon" mode="aspectFit"></image>
						</view>
						<view class="feature-info">
							<text class="feature-title">{{ feature.title }}</text>
							<text class="feature-desc">{{ feature.description }}</text>
						</view>
					</view>
					<uni-icons type="right" size="16" color="#999"></uni-icons>
				</view>
			</view>
		</view>
		
		<!-- 统计数据区域 -->
		<view class="content-section">
			<view class="section-title">系统数据</view>
			<view class="stats-section">
				<view class="stat-card" v-for="(stat, index) in statistics" :key="index">
					<text class="stat-value">{{ stat.value }}</text>
					<text class="stat-title">{{ stat.title }}</text>
					<text class="stat-desc">{{ stat.description }}</text>
				</view>
			</view>
		</view>
		
		<!-- 底部版权信息 -->
		<view class="footer">
			<text class="copyright">Copyright © 2023-2025 鹿津愉</text>
		</view>
	</view>
</template>

<script>
export default {
	data() {
		return {
			title: '手语识别系统',
			features: [
				{
					title: '图片识别',
					description: '上传手语图片，快速识别并翻译',
					icon: '/static/tabbar/图片.png',
					path: '/pages/image/image'
				},
				{
					title: '视频识别',
					description: '分析手语视频，实时翻译手语动作',
					icon: '/static/tabbar/Videocam.png',
					path: '/pages/video/video'
				},
				{
					title: '摄像头识别',
					description: '通过摄像头实时捕捉并翻译手语',
					icon: '/static/tabbar/摄像头.png',
					path: '/pages/camera/camera'
				}
			],
			statistics: [
				{
					title: '识别准确率',
					value: '95%',
					description: '基于最新YOLO模型训练'
				},
				{
					title: '支持手语数量',
					value: '200+',
					description: '覆盖日常交流常用手语'
				},
				{
					title: '用户数量',
					value: '1000+',
					description: '来自全国各地的用户'
				}
			]
		}
	},
	onLoad() {
		this.checkLogin();
	},
	methods: {
		checkLogin() {
			const token = uni.getStorageSync('token');
			if (!token) {
				uni.reLaunch({
					url: '/pages/login/login'
				});
			}
		},
		
		// 页面跳转
		navigateTo(path) {
			uni.navigateTo({
				url: path
			});
		}
	}
}
</script>

<style>
.home-container {
	min-height: 100vh;
	background-color: #f5f7fa;
	display: flex;
	flex-direction: column;
	padding-top: var(--status-bar-height);
}

/* 欢迎区域样式 */
.welcome-section {
	background: linear-gradient(135deg, #3a7bd5, #00d2ff);
	padding: 80rpx 30rpx 60rpx;
	border-radius: 0 0 40rpx 40rpx;
	margin-bottom: 30rpx;
	padding-top: calc(80rpx + constant(safe-area-inset-top));
	padding-top: calc(80rpx + env(safe-area-inset-top));
}

.welcome-content {
	display: flex;
	flex-direction: column;
	align-items: center;
	margin-top: 20rpx;
}

.logo {
	width: 120rpx;
	height: 120rpx;
	margin-bottom: 20rpx;
}

.title {
	font-size: 40rpx;
	font-weight: bold;
	color: #ffffff;
	margin-bottom: 10rpx;
}

.subtitle {
	font-size: 28rpx;
	color: rgba(255, 255, 255, 0.9);
}

/* 内容区域通用样式 */
.content-section {
	padding: 0 30rpx;
	margin-bottom: 30rpx;
}

.section-title {
	font-size: 32rpx;
	font-weight: bold;
	color: #333;
	margin-bottom: 20rpx;
	padding-left: 20rpx;
	border-left: 8rpx solid #3a7bd5;
}

/* 功能卡片样式 */
.feature-cards {
	display: flex;
	flex-direction: column;
	gap: 20rpx;
}

.feature-card {
	background-color: #fff;
	border-radius: 16rpx;
	padding: 30rpx;
	display: flex;
	align-items: center;
	justify-content: space-between;
	box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.05);
	transition: transform 0.2s;
}

.feature-card:active {
	transform: scale(0.98);
}

.card-content {
	display: flex;
	align-items: center;
	flex: 1;
}

.feature-icon {
	width: 80rpx;
	height: 80rpx;
	margin-right: 20rpx;
}

.feature-icon image {
	width: 100%;
	height: 100%;
}

.feature-info {
	flex: 1;
}

.feature-title {
	font-size: 32rpx;
	font-weight: bold;
	color: #333;
	margin-bottom: 8rpx;
}

.feature-desc {
	font-size: 24rpx;
	color: #666;
}

/* 统计数据样式 */
.stats-section {
	display: flex;
	justify-content: space-between;
	flex-wrap: wrap;
	gap: 20rpx;
}

.stat-card {
	background-color: #fff;
	border-radius: 16rpx;
	padding: 24rpx;
	flex: 1;
	min-width: calc(33.33% - 14rpx);
	box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.05);
	display: flex;
	flex-direction: column;
	align-items: center;
}

.stat-value {
	font-size: 36rpx;
	font-weight: bold;
	color: #3a7bd5;
	margin-bottom: 8rpx;
}

.stat-title {
	font-size: 24rpx;
	color: #333;
	margin-bottom: 8rpx;
}

.stat-desc {
	font-size: 20rpx;
	color: #999;
	text-align: center;
}

/* 底部版权信息 */
.footer {
	margin-top: auto;
	padding: 30rpx 0;
	text-align: center;
}

.copyright {
	font-size: 24rpx;
	color: #999;
}

/* 响应式布局调整 */
@media screen and (min-width: 768px) {
	.feature-cards {
		flex-direction: row;
		flex-wrap: wrap;
	}
	
	.feature-card {
		width: calc(50% - 10rpx);
	}
	
	.stat-card {
		min-width: calc(33.33% - 14rpx);
	}
}

@media screen and (max-width: 375px) {
	.welcome-section {
		padding: 60rpx 20rpx 50rpx;
		padding-top: calc(60rpx + constant(safe-area-inset-top));
	}
	
	.content-section {
		padding: 0 20rpx;
	}
	
	.feature-card {
		padding: 20rpx;
	}
	
	.stat-card {
		padding: 16rpx;
	}
	
	.title {
		font-size: 36rpx;
	}
	
	.subtitle {
		font-size: 24rpx;
	}
}
</style>
