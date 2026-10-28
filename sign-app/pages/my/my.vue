<template>
	<view class="my-container">
		<!-- 用户信息卡片 -->
		<view class="user-card">
			<view class="avatar-box" @tap="goToUserInfo">
				<image 
					v-if="imageUrl" 
					:src="getServerUrl() + 'media/userAvatar/' + userInfo.avatar" 
					class="avatar" 
					mode="aspectFill"
				/>
				<image 
					v-else 
					src="/static/default-avatar.png" 
					class="avatar" 
					mode="aspectFill"
				/>
			</view>
			<view class="user-info">
				<view class="username">{{userInfo.username || '未登录'}}</view>
				<view class="user-role">{{userRoleName}}</view>
			</view>
		</view>
		
		<!-- 功能菜单 -->
		<view class="menu-list">
			<view class="menu-item" @tap="goToUserInfo">
				<view class="menu-icon">
					<uni-icons type="compose" size="30"></uni-icons>
					
				</view>
				<view class="menu-text">个人资料</view>
				
				<view class="menu-arrow">
						<image  style="width: 50rpx;height: 50rpx;"src="/static/个人资料.png" mode="aspectFit"></image>
					
				</view>
			</view>
			
			<view class="menu-item" @tap="goToSetting">
				<view class="menu-icon">
					<uni-icons type="tune" size="30"></uni-icons>
				</view>
				<view class="menu-text">系统设置</view>
				<view class="menu-arrow">
						<image  style="width: 50rpx;height: 50rpx;"src="/static/设置.png" mode="aspectFit"></image>
				</view>
			</view>
			
			<view class="menu-item" @tap="goToAbout">
				<view class="menu-icon">
					<uni-icons type="info" size="30"></uni-icons>
				</view>
				<view class="menu-text">关于我们</view>
				<view class="menu-arrow">
						<image  style="width: 50rpx;height: 50rpx;"src="/static/关于我们.png" mode="aspectFit"></image>
				</view>
			</view>
		</view>
		
		<!-- 退出登录按钮 -->
		<view class="logout-btn" @tap="handleLogout">
			<text>退出登录</text>
		</view>
	</view>
</template>

<script>
import request from '../../utils/request.js';
import { getServerUrl } from '../../utils/request.js';

export default {
	data() {
		return {
			userInfo: {},
			imageUrl: '',
			userRoleName: '普通用户'
		}
	},
	onShow() {
		// 从本地存储获取用户信息
		const userInfo = JSON.parse(uni.getStorageSync('currentUser'));
		if(userInfo) {
			this.userInfo = userInfo;
			// 设置头像URL
			if(this.userInfo.avatar) {
				this.imageUrl = this.userInfo.avatar;
			} else {
				this.imageUrl = '';
			}
			if(userInfo.roles && userInfo.roles.length > 0) {
				this.userRoleName = userInfo.roles[0].roleName;
			}
		}
	},
	methods: {
		// 获取服务器URL
		getServerUrl() {
			return getServerUrl();
		},
		
		// 跳转到个人资料页面
		goToUserInfo() {
			uni.navigateTo({
				url: '/pages/userInfo/userInfo'
			});
		},

		// 跳转到设置页面
		goToSetting() {
			uni.navigateTo({
				url: '/pages/setting/setting'
			});
		},

		// 跳转到关于页面
		goToAbout() {
			uni.navigateTo({
				url: '/pages/about/about'
			});
		},

		// 退出登录
		handleLogout() {
			uni.showModal({
				title: '提示',
				content: '确定要退出登录吗？',
				success: (res) => {
					if(res.confirm) {
						uni.clearStorageSync();
						uni.reLaunch({
							url: '/pages/login/login'
						});
					}
				}
			});
		}
	}
}
</script>

<style>
.my-container {
	min-height: 100vh;
	background-color: #f5f5f5;
	padding-bottom: 40rpx;
}

.user-card {
	background: linear-gradient(135deg, #007AFF, #1989fa);
	padding: 40rpx 30rpx;
	display: flex;
	align-items: center;
}

.avatar-box {
	width: 120rpx;
	height: 120rpx;
	border-radius: 60rpx;
	overflow: hidden;
	border: 1px dashed #d9d9d9;
	margin-right: 30rpx;
	background-color: #fff;
	cursor: pointer;
	position: relative;
}

.avatar-box:hover {
	border-color: #409eff;
}

.avatar {
	width: 100%;
	height: 100%;
	display: block;
}

.user-info {
	flex: 1;
}

.username {
	font-size: 36rpx;
	color: #fff;
	font-weight: bold;
	margin-bottom: 10rpx;
}

.user-role {
	font-size: 24rpx;
	color: rgba(255, 255, 255, 0.8);
}

.menu-list {
	background-color: #fff;
	margin: 20rpx;
	border-radius: 16rpx;
	padding: 0 20rpx;
}

.menu-item {
	display: flex;
	align-items: center;
	padding: 30rpx 0;
	border-bottom: 1rpx solid #eee;
}

.menu-item:last-child {
	border-bottom: none;
}

.menu-icon {
	width: 40rpx;
	margin-right: 20rpx;
}

.menu-icon .iconfont {
	font-size: 36rpx;
	color: #007AFF;
}

.menu-text {
	flex: 1;
	font-size: 28rpx;
	color: #333;
}

.menu-arrow {
	color: #999;

	
}

.menu-arrow .iconfont {
	font-size: 24rpx;
}

.logout-btn {
	margin: 60rpx 40rpx;
	height: 90rpx;
	line-height: 90rpx;
	text-align: center;
	background: linear-gradient(to right, #ff6000, #ff9500);
	color: #fff;
	font-size: 32rpx;
	border-radius: 45rpx;
	box-shadow: 0 4rpx 12rpx rgba(255, 96, 0, 0.3);
}

.logout-btn:active {
	transform: scale(0.98);
	opacity: 0.9;
}
</style>