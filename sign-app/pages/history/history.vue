<template>
	<view class="history-container">
		<!-- 页面标题 -->
		<view class="page-header">
			<text class="page-title">历史记录</text>
		</view>
		
		<!-- 历史记录类型选择 -->
		<view class="history-types">
			<!-- 图片识别历史 -->
			<view class="history-card" @tap="navigateTo('/pages/imageHistory/imageHistory')">
				<view class="card-icon">
					<uni-icons type="image" size="30"></uni-icons>
					
				</view>
				<view class="card-content">
					<text class="card-title">图片识别历史</text>
					<text class="card-desc">查看所有图片手语识别记录</text>
				</view>

				<uni-icons type="images" size="30"></uni-icons>
			</view>
			
			<!-- 摄像头识别历史 -->
			<view class="history-card" @tap="navigateTo('/pages/cameraHistory/cameraHistory')">
				<view class="card-icon">
					<uni-icons type="camera" size="30"></uni-icons>
				</view>
				<view class="card-content">
					<text class="card-title">摄像头识别历史</text>
					<text class="card-desc">查看实时摄像头识别记录</text>
				</view>
				<uni-icons type="camera-filled" size="30"></uni-icons>
			</view>
			
			<!-- 视频识别历史 -->
			<view class="history-card" @tap="navigateTo('/pages/videoHistory/videoHistory')">
				<view class="card-icon">
					<uni-icons type="videocam" size="30"></uni-icons>
				</view>
				<view class="card-content">
					<text class="card-title">视频识别历史</text>
					<text class="card-desc">查看所有视频手语识别记录</text>
				</view>
				<uni-icons type="videocam-filled" size="30"></uni-icons>
			</view>
		</view>
	</view>
</template>

<script>
export default {
	data() {
		return {}
	},
	onLoad() {
		// 检查登录状态
		this.checkLoginStatus();
	},
	methods: {
		// 检查登录状态
		checkLoginStatus() {
			const token = uni.getStorageSync('token');
			if (!token) {
				// 未登录，跳转到登录页面
				uni.navigateTo({
					url: '/pages/login/login?redirect=/pages/history/history'
				});
			}
		},
		
		// 页面导航
		navigateTo(url) {
			uni.navigateTo({
				url: url
			});
		}
	}
}
</script>

<style lang="scss">
.history-container {
	padding: 30rpx;
	background-color: #f5f5f5;
	min-height: 100vh;
}

.page-header {
	margin-bottom: 40rpx;
}

.page-title {
	font-size: 36rpx;
	font-weight: bold;
	color: #333;
}

.history-types {
	display: flex;
	flex-direction: column;
	gap: 30rpx;
}

.history-card {
	background-color: #fff;
	border-radius: 15rpx;
	padding: 30rpx;
	box-shadow: 0 4rpx 15rpx rgba(0, 0, 0, 0.05);
	display: flex;
	align-items: center;
	position: relative;
	transition: transform 0.2s;
}

.history-card:active {
	transform: scale(0.98);
}

.card-icon {
	width: 80rpx;
	height: 80rpx;
	border-radius: 40rpx;
	background-color: #f0f5ff;
	display: flex;
	justify-content: center;
	align-items: center;
	margin-right: 20rpx;
}

.card-icon .iconfont {
	font-size: 40rpx;
	color: #1890ff;
}

.card-icon .icon-camera {
	color: #52c41a;
}

.card-icon .icon-video {
	color: #fa8c16;
}

.card-content {
	flex: 1;
}

.card-title {
	font-size: 30rpx;
	font-weight: bold;
	color: #333;
	margin-bottom: 6rpx;
}

.card-desc {
	font-size: 24rpx;
	color: #999;
}

.icon-right {
	font-size: 36rpx;
	color: #ccc;
}

/* 图标字体 */
@font-face {
	font-family: 'iconfont';
	src: url('data:application/x-font-woff2;charset=utf-8;base64,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') format('woff2');
}

.iconfont {
	font-family: "iconfont" !important;
	font-size: 32rpx;
	font-style: normal;
	-webkit-font-smoothing: antialiased;
	-moz-osx-font-smoothing: grayscale;
	color: #999;
}

.icon-picture:before {
	content: "\e6bd";
}

.icon-camera:before {
	content: "\e6ac";
}

.icon-video:before {
	content: "\e7c8";
}

.icon-right:before {
	content: "\e7eb";
}
</style>


