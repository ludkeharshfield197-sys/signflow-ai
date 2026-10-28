<template>
	<view class="userinfo-container">
		<!-- 头像区域 -->
		<view class="avatar-section">
			<view class="avatar-wrapper" @tap="changeAvatar">
				<image 
					v-if="userInfo.avatar" 
					:src="getServerUrl() + 'media/userAvatar/' + userInfo.avatar" 
					class="avatar"
					mode="aspectFill"
				/>
				<image 
					v-else 
					class="avatar"
					src="/static/default-avatar.png"
					mode="aspectFill"
				/>
				<view class="avatar-edit-icon">
					<text class="iconfont icon-camera"></text>
					<text>更换头像</text>
				</view>
			</view>
		</view>
		
		<!-- 信息表单 -->
		<view class="form-section">
			<view class="form-item">
				<text class="form-label">用户名</text>
				<input 
					class="form-input" 
					type="text" 
					v-model="userInfo.username"
					placeholder="请输入用户名"
				/>
			</view>
			
			<view class="form-item">
				<text class="form-label">手机号码</text>
				<input 
					class="form-input" 
					type="number" 
					v-model="userInfo.phonenumber"
					placeholder="请输入手机号码"
					maxlength="11"
				/>
			</view>
			
			<view class="form-item">
				<text class="form-label">邮箱地址</text>
				<input 
					class="form-input" 
					type="text" 
					v-model="userInfo.email"
					placeholder="请输入邮箱地址"
				/>
			</view>
		</view>
		
		<!-- 按钮组 -->
		<view class="button-group">
			<button class="pwd-button" @tap="goToChangePassword">
				修改密码
			</button>
			<button class="save-button" @tap="saveUserInfo" :loading="loading">
				保存修改
			</button>
		</view>
	</view>
</template>

<script>
import request, { getServerUrl } from '../../utils/request.js';

export default {
	data() {
		return {
			userInfo: {
				id: '',
				username: '',
				phonenumber: '',
				email: '',
				avatar: ''
			},
			loading: false
		}
	},
	onLoad() {
		const userInfo = JSON.parse(uni.getStorageSync('currentUser'));
		if(userInfo) {
			this.userInfo = userInfo;
		}
	},
	methods: {
		getServerUrl() {
			return getServerUrl();
		},
		
		// 更换头像
		changeAvatar() {
			uni.chooseImage({
				count: 1,
				success: async (chooseRes) => {
					try {
						// 创建上传任务
						const uploadTask = uni.uploadFile({
							url: getServerUrl() + 'user/uploadImage',
							filePath: chooseRes.tempFilePaths[0],
							name: 'avatar',
							formData: {
								id: this.userInfo.id
							},
							header: {
								'AUTHORIZATION': uni.getStorageSync('token')
							},
							success: async (uploadRes) => {
								console.log('上传响应:', uploadRes);
								const result = JSON.parse(uploadRes.data);
								if(result.code === 200) {
									// 更新头像 - 修改请求方式
									try {
										const updateRes = await request.request({
											url: 'user/updateAvatar',
											method: 'POST',
											data: {
												id: this.userInfo.id,
												avatar: result.title
											},
											header: {
												'Content-Type': 'application/json'
											}
										});
										
										if(updateRes.code === 200) {
											this.userInfo.avatar = result.title;
											// 更新本地存储
											uni.setStorageSync('currentUser', JSON.stringify(this.userInfo));
											uni.showToast({
												title: '头像更新成功',
												icon: 'success'
											});
										}
									} catch(err) {
										console.error('更新头像失败:', err);
										uni.showToast({
											title: '头像更新失败',
											icon: 'none'
										});
									}
								} else {
									uni.showToast({
										title: result.msg || '上传失败',
										icon: 'none'
									});
								}
							},
							fail: (err) => {
								console.error('上传失败:', err);
								uni.showToast({
									title: '上传失败',
									icon: 'none'
								});
							}
						});
						
						// 监听上传进度
						uploadTask.onProgressUpdate((res) => {
							console.log('上传进度', res.progress);
						});
						
					} catch(err) {
						console.error('选择图片失败:', err);
						uni.showToast({
							title: '上传失败',
							icon: 'none'
						});
					}
				}
			});
		},
		
		// 跳转到修改密码页面
		goToChangePassword() {
			uni.navigateTo({
				url: '/pages/changePassword/changePassword'
			});
		},
		
		// 验证手机号
		validatePhone(phone) {
			return /^1[3-9]\d{9}$/.test(phone);
		},
		
		// 验证邮箱
		validateEmail(email) {
			return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
		},
		
		// 保存用户信息
		async saveUserInfo() {
			// 表单验证
			if(!this.userInfo.username) {
				uni.showToast({
					title: '用户名不能为空',
					icon: 'none'
				});
				return;
			}
			
			// 检查用户名是否已存在
			try {
				const checkRes = await request.request({
					url: 'user/check',
					method: 'POST',
					data: {
						username: this.userInfo.username
					}
				});
				
				if(checkRes.code === 500) {
					uni.showToast({
						title: '用户名已存在',
						icon: 'none'
					});
					return;
				}
			} catch(err) {
				console.error('检查用户名失败:', err);
				uni.showToast({
					title: '验证用户名失败',
					icon: 'none'
				});
				return;
			}
			
			if(this.userInfo.phonenumber && !this.validatePhone(this.userInfo.phonenumber)) {
				uni.showToast({
					title: '请输入正确的手机号',
					icon: 'none'
				});
				return;
			}
			
			if(this.userInfo.email && !this.validateEmail(this.userInfo.email)) {
				uni.showToast({
					title: '请输入正确的邮箱地址',
					icon: 'none'
				});
				return;
			}
			
			this.loading = true;
			try {
				// 参考 PC 端，只发送必要的字段
				const formData = {
					id: this.userInfo.id,
					username: this.userInfo.username,
					password: this.userInfo.password || '',
					email: this.userInfo.email || '',
					phonenumber: this.userInfo.phonenumber || '',
					avatar: this.userInfo.avatar || '',
					status: this.userInfo.status || '0',
					create_time: this.userInfo.create_time,
					update_time: this.userInfo.update_time,
					login_date: this.userInfo.login_date || '',
					remark: this.userInfo.remark || ''
				};
				
				const res = await request.request({
					url: 'user/save',
					method: 'POST',
					header: {
						'Content-Type': 'application/json'  // 改为 JSON 格式
					},
					data: JSON.stringify(formData)  // 将数据转换为 JSON 字符串
				});
				
				if(res.code === 200) {
					// 更新本地存储
					uni.setStorageSync('currentUser', JSON.stringify(this.userInfo));
					uni.showToast({
						title: '保存成功',
						icon: 'success'
					});
					setTimeout(() => {
						uni.navigateBack();
					}, 1500);
				} else {
					uni.showToast({
						title: res.msg || '保存失败',
						icon: 'none'
					});
				}
			} catch(err) {
				console.error('保存失败:', err);
				uni.showToast({
					title: '保存失败',
					icon: 'none'
				});
			} finally {
				this.loading = false;
			}
		}
	}
}
</script>

<style>
.userinfo-container {
	min-height: 100vh;
	background-color: #f5f5f5;
	padding-bottom: 40rpx;
}

.avatar-section {
	background-color: #fff;
	padding: 40rpx 0;
	display: flex;
	justify-content: center;
	margin-bottom: 20rpx;
}

.avatar-wrapper {
	position: relative;
	width: 180rpx;
	height: 180rpx;
	border-radius: 90rpx;
	border: 1px dashed #d9d9d9;
	overflow: hidden;
	cursor: pointer;
}

.avatar-wrapper:hover {
	border-color: #409eff;
}

.avatar {
	width: 100%;
	height: 100%;
	display: block;
}

.avatar-edit-icon {
	position: absolute;
	bottom: 0;
	left: 0;
	right: 0;
	background-color: rgba(0, 0, 0, 0.6);
	padding: 8rpx 0;
	text-align: center;
	color: #fff;
	font-size: 24rpx;
}

.form-section {
	background-color: #fff;
	padding: 0 30rpx;
	margin: 20rpx;
	border-radius: 12rpx;
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
	width: 160rpx;
	font-size: 28rpx;
	color: #666;
}

.form-input {
	flex: 1;
	height: 60rpx;
	font-size: 28rpx;
	color: #333;
}

.form-text {
	flex: 1;
	font-size: 28rpx;
	color: #333;
}

.button-group {
	padding: 40rpx 20rpx;
	display: flex;
	flex-direction: column;
	gap: 20rpx;
}

.pwd-button {
	width: 100%;
	height: 90rpx;
	line-height: 90rpx;
	background: linear-gradient(to right, #ff9500, #ff6000);
	color: #fff;
	font-size: 32rpx;
	border-radius: 45rpx;
	border: none;
}

.save-button {
	width: 100%;
	height: 90rpx;
	line-height: 90rpx;
	background: linear-gradient(to right, #007AFF, #1989fa);
	color: #fff;
	font-size: 32rpx;
	border-radius: 45rpx;
	border: none;
}

.pwd-button:active,
.save-button:active {
	opacity: 0.9;
}
</style>