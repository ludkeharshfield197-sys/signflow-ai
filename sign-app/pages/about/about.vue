<template>
	<view class="about-container">
		<!-- 应用信息 -->
		<view class="app-info">
			<image class="app-logo" src="/static/logo.png" mode="aspectFit"></image>
			<view class="app-name">手语识别系统</view>
			<view class="app-version">版本 1.0.0</view>
		</view>
		
		<!-- 应用介绍 -->
		<view class="info-section">
			<view class="section-title">应用介绍</view>
			<view class="section-content">
				<text class="section-text">手语识别系统是一款基于YOLO目标检测的手语翻译工具，旨在帮助听障人士与他人进行更便捷的沟通。本应用是完整系统的移动端部分，支持图像识别、视频识别和实时摄像头识别等多种手语输入方式，提供便捷的手语翻译服务。</text>
			</view>
		</view>
		
		<!-- 功能特色 -->
		<view class="info-section">
			<view class="section-title">功能特色</view>
			<view class="section-content">
				<view class="feature-item">
					<uni-icons type="camera" size="18" color="#007AFF"></uni-icons>
					<text class="feature-text">实时摄像头手语识别，支持连续动作分析</text>
				</view>
				<view class="feature-item">
					<uni-icons type="image" size="18" color="#007AFF"></uni-icons>
					<text class="feature-text">图像手语识别，快速翻译单幅手语图像</text>
				</view>
				<view class="feature-item">
					<uni-icons type="videocam" size="18" color="#007AFF"></uni-icons>
					<text class="feature-text">视频手语识别，处理已有手语视频文件</text>
				</view>
				<view class="feature-item">
					<uni-icons type="folder" size="18" color="#007AFF"></uni-icons>
					<text class="feature-text">历史记录查询，方便回顾之前的识别结果</text>
				</view>
				<view class="feature-item">
					<uni-icons type="chatboxes" size="18" color="#007AFF"></uni-icons>
					<text class="feature-text">自然语言生成，将手语动作转换为流畅句子</text>
				</view>
			</view>
		</view>
		
		<!-- 技术栈 -->
		<view class="info-section">
			<view class="section-title">技术栈</view>
			<view class="section-content">
				<view class="tech-item">
					<text class="tech-category">前端框架：</text>
					<text class="tech-value">uni-app、Vue 3.x</text>
				</view>
				<view class="tech-item">
					<text class="tech-category">后端框架：</text>
					<text class="tech-value">Django、Django REST Framework</text>
				</view>
				<view class="tech-item">
					<text class="tech-category">AI模型：</text>
					<text class="tech-value">YOLOv8目标检测模型</text>
				</view>
				<view class="tech-item">
					<text class="tech-category">实时通信：</text>
					<text class="tech-value">WebSocket (Django Channels)</text>
				</view>
			</view>
		</view>
		
		<!-- 开发团队 -->
		<view class="info-section">
			<view class="section-title">开发团队</view>
			<view class="section-content">
				<text class="section-text">本应用由鹿津愉及其团队开发完成，采用前后端分离架构，包括Web端和移动端应用，共同连接统一的后端服务。</text>
			</view>
		</view>
		
		<!-- 联系方式 -->
		<view class="info-section">
			<view class="section-title">联系方式</view>
			<view class="section-content">
				<view class="contact-item">
					<text class="contact-label">邮箱：</text>
					<text class="contact-value">1143016031@qq.com</text>
				</view>
				<view class="contact-item">
					<text class="contact-label">电话：</text>
					<text class="contact-value">18810979550</text>
				</view>
				<view class="contact-item">
					<text class="contact-label">网站：</text>
					<text class="contact-value">www.ljy.com</text>
				</view>
			</view>
		</view>
		
		<!-- 版权信息 -->
		<view class="copyright">
			<text>Copyright © 2023-2025 鹿津愉 版权所有.</text>
		</view>
	</view>
</template>

<script>
export default {
	data() {
		return {}
	},
	methods: {}
}
</script>

<style>
.about-container {
	display: flex;
	flex-direction: column;
	min-height: 100vh;
	background-color: #f5f5f5;
	padding-bottom: 40rpx;
}

.app-info {
	display: flex;
	flex-direction: column;
	align-items: center;
	padding: 60rpx 0;
	background-color: #fff;
}

.app-logo {
	width: 160rpx;
	height: 160rpx;
	margin-bottom: 20rpx;
}

.app-name {
	font-size: 36rpx;
	font-weight: bold;
	color: #333;
	margin-bottom: 10rpx;
}

.app-version {
	font-size: 28rpx;
	color: #999;
}

.info-section {
	background-color: #fff;
	margin-top: 20rpx;
	padding: 30rpx;
}

.section-title {
	font-size: 32rpx;
	font-weight: bold;
	color: #333;
	margin-bottom: 20rpx;
	border-left: 8rpx solid #007AFF;
	padding-left: 20rpx;
}

.section-content {
	padding: 0 10rpx;
}

.section-text {
	font-size: 28rpx;
	color: #666;
	line-height: 1.6;
}

.contact-item {
	display: flex;
	margin-bottom: 10rpx;
}

.contact-label {
	font-size: 28rpx;
	color: #333;
	width: 100rpx;
}

.contact-value {
	font-size: 28rpx;
	color: #666;
}

.copyright {
	text-align: center;
	padding: 40rpx 0;
	font-size: 24rpx;
	color: #999;
	margin-top: auto;
}

/* 新增样式 */
.feature-item {
	display: flex;
	align-items: center;
	margin-bottom: 16rpx;
}

.feature-text {
	font-size: 28rpx;
	color: #666;
	margin-left: 12rpx;
}

.tech-item {
	margin-bottom: 12rpx;
}

.tech-category {
	font-size: 28rpx;
	color: #333;
	font-weight: 500;
}

.tech-value {
	font-size: 28rpx;
	color: #666;
}
</style>