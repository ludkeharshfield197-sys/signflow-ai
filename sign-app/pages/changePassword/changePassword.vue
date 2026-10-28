<template>
	<view class="change-password-container">
		<!-- 密码表单 -->
		<view class="form-section">
			<view class="form-item">
				<text class="form-label">原密码</text>
				<input class="form-input" type="password" v-model="oldPassword" placeholder="请输入原密码" />
			</view>
			
			<view class="form-item">
				<text class="form-label">新密码</text>
				<input class="form-input" type="password" v-model="newPassword" placeholder="请输入新密码" />
			</view>
			
			<view class="form-item">
				<text class="form-label">确认密码</text>
				<input class="form-input" type="password" v-model="confirmPassword" placeholder="请再次输入新密码" />
			</view>
		</view>
		
		
		<!-- 提交按钮 -->
		<view class="action-section">
			<view class="action-button submit-button" @tap="handleChangePassword">
				<text>确认修改</text>
			</view>
		</view>
	</view>
</template>

<script>
import request from '../../utils/request.js';

export default {
	data() {
		return {
			oldPassword: '',
			newPassword: '',
			confirmPassword: '',
			userInfo: null
		}
	},
	onLoad() {
		// 获取当前用户信息
		this.userInfo = JSON.parse(uni.getStorageSync('currentUser'));
	},
	methods: {
		// 验证密码
		validatePassword() {
			if(!this.oldPassword) {
				uni.showToast({
					title: '请输入原密码',
					icon: 'none'
				});
				return false;
			}
			
			if(!this.newPassword) {
				uni.showToast({
					title: '请输入新密码',
					icon: 'none'
				});
				return false;
			}
			
			if(this.newPassword.length < 6) {
				uni.showToast({
					title: '新密码长度不能少于6位',
					icon: 'none'
				});
				return false;
			}
			
			if(this.newPassword !== this.confirmPassword) {
				uni.showToast({
					title: '两次输入的密码不一致',
					icon: 'none'
				});
				return false;
			}
			
			return true;
		},
		
		// 修改密码
		async handleChangePassword() {
			if(!this.validatePassword()) {
				return;
			}
			
			try {
				// 参考 PC 端实现
				const formData = {
					id: this.userInfo.id,
					oldPassword: this.oldPassword,
					newPassword: this.newPassword
				};
				
				const res = await request.request({
					url: 'user/updateUserPwd',
					method: 'POST',
					header: {
						'Content-Type': 'application/json'
					},
					data: JSON.stringify(formData)
				});
				
				if(res.code === 200) {
					uni.showToast({
						title: '密码修改成功',
						icon: 'success'
					});
					
					// 清除登录信息并返回登录页
					setTimeout(() => {
						uni.clearStorageSync();
						uni.reLaunch({
							url: '/pages/login/login'
						});
					}, 1500);
				} else {
					uni.showToast({
						title: res.msg || '原密码错误',
						icon: 'none'
					});
				}
			} catch(err) {
				console.error('修改密码失败:', err);
				uni.showToast({
					title: '修改失败，请重试',
					icon: 'none'
				});
			}
		}
	}
}
</script>

<style>
.change-password-container {
	display: flex;
	flex-direction: column;
	min-height: 100vh;
	background-color: #f5f5f5;
	padding-bottom: 40rpx;
}

.form-section {
	background-color: #fff;
	padding: 20rpx 30rpx;
	margin: 20rpx 20rpx 30rpx;
	border-radius: 12rpx;
	box-shadow: 0 2rpx 10rpx rgba(0, 0, 0, 0.05);
}

.form-item {
	display: flex;
	align-items: center;
	padding: 30rpx 0;
	border-bottom: 1px solid #eee;
}

.form-item:last-child {
	border-bottom: none;
}

.form-label {
	width: 150rpx;
	font-size: 30rpx;
	color: #333;
}

.form-input {
	flex: 1;
	height: 60rpx;
	font-size: 30rpx;
}

.tips-section {
	padding: 0 30rpx;
	margin-bottom: 40rpx;
}

.tips-title {
	font-size: 28rpx;
	color: #666;
	margin-bottom: 10rpx;
	display: block;
}

.tips-text {
	font-size: 26rpx;
	color: #999;
	margin-bottom: 6rpx;
	display: block;
}

.action-section {
	margin: 0 20rpx 30rpx;
}

.action-button {
	height: 90rpx;
	line-height: 90rpx;
	text-align: center;
	border-radius: 45rpx;
	font-size: 32rpx;
	color: #fff;
}

.submit-button {
	background-color: #007AFF;
}
</style>