<template>
	<view class="setting-container">
		<!-- 设置列表 -->
		<view class="setting-list">
			<!-- 通用设置 -->
			<view class="setting-group">
				<view class="setting-group-title">通用设置</view>
				<!-- 语言设置 -->
				<view class="setting-item">
					<view class="setting-label-container">
						<uni-icons type="language" size="20" color="#666"></uni-icons>
						<text class="setting-label">语言</text>
					</view>
					<picker @change="changeLanguage" :value="languageIndex" :range="languageOptions">
						<view class="picker-value">
							{{languageOptions[languageIndex]}}
							<uni-icons type="right" size="16" color="#ccc"></uni-icons>
						</view>
					</picker>
				</view>
			</view>
			
			<!-- 数据管理 -->
			<view class="setting-group">
				<view class="setting-group-title">数据管理</view>
				<!-- 清除缓存 -->
				<view class="setting-item" @tap="clearCache">
					<view class="setting-label-container">
						<uni-icons type="trash" size="20" color="#666"></uni-icons>
						<text class="setting-label">清除缓存</text>
					</view>
					<view class="setting-value-container">
						<text class="setting-value">{{cacheSize}}</text>
						<uni-icons type="right" size="16" color="#ccc"></uni-icons>
					</view>
				</view>
			</view>
			
			<!-- 关于应用 -->
			<view class="setting-group">
				<view class="setting-item" @tap="goToAbout">
					<view class="setting-label-container">
						<uni-icons type="info" size="20" color="#666"></uni-icons>
						<text class="setting-label">关于应用</text>
					</view>
					<view class="setting-value-container">
						<uni-icons type="right" size="16" color="#ccc"></uni-icons>
					</view>
				</view>
			</view>
			
			<!-- 退出登录 -->
			<view class="setting-group logout-group">
				<view class="setting-item" @tap="logout">
					<text class="logout-text">退出登录</text>
				</view>
			</view>
		</view>
		
		<!-- 版本信息 -->
		<view class="version-info">
			<text>当前版本: v1.0.0</text>
		</view>
	</view>
</template>

<script>
export default {
	data() {
		return {
			languageOptions: ['简体中文', '英文'],
			languageIndex: 0,
			cacheSize: '计算中...',
			settings: {
				language: 'zh-CN'
			}
		}
	},
	onLoad() {
		// 检查登录状态
		this.checkLoginStatus();
		// 加载本地存储的设置
		this.loadSettings();
		// 计算缓存大小
		this.calculateCacheSize();
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
						url: '/pages/login/login?redirect=/pages/setting/setting'
					});
				}, 1500);
				return;
			}
		},
		
		// 加载设置
		loadSettings() {
			const settingsStr = uni.getStorageSync('appSettings');
			if (settingsStr) {
				try {
					const savedSettings = JSON.parse(settingsStr);
					this.settings = { ...this.settings, ...savedSettings };
					
					// 设置语言索引
					if(this.settings.language === 'en-US') {
						this.languageIndex = 1;
					} else {
						this.languageIndex = 0;
					}
				} catch (e) {
					console.error('解析设置失败:', e);
				}
			}
		},
		
		// 保存设置
		saveSettings() {
			uni.setStorageSync('appSettings', JSON.stringify(this.settings));
			uni.showToast({
				title: '设置已保存',
				icon: 'success',
				duration: 1500
			});
		},
		
		// 更改语言
		changeLanguage(e) {
			this.languageIndex = parseInt(e.detail.value);
			this.settings.language = this.languageIndex === 0 ? 'zh-CN' : 'en-US';
			this.saveSettings();
			
			// 提示需要重启应用
			uni.showModal({
				title: '提示',
				content: '语言设置已保存，重启应用后生效',
				showCancel: false
			});
		},
		
		// 计算缓存大小
		calculateCacheSize() {
			// 计算缓存大小
			uni.getStorageInfo({
				success: (res) => {
					// 转换为合适的单位
					const size = res.currentSize;
					if (size < 1024) {
						this.cacheSize = size + 'B';
					} else if (size < 1024 * 1024) {
						this.cacheSize = (size / 1024).toFixed(2) + 'KB';
					} else {
						this.cacheSize = (size / (1024 * 1024)).toFixed(2) + 'MB';
					}
				},
				fail: () => {
					this.cacheSize = '未知';
				}
			});
		},
		
		// 清除缓存
		clearCache() {
			uni.showModal({
				title: '提示',
				content: '确定要清除缓存吗？这将清除所有本地存储的设置和数据(不包括登录信息)。',
				success: (res) => {
					if (res.confirm) {
						// 显示加载中
						uni.showLoading({
							title: '清除中...'
						});
						
						// 清除缓存
						setTimeout(() => {
							// 保留登录状态和用户数据
							const token = uni.getStorageSync('token');
							const userInfo = uni.getStorageSync('currentUser');
							
							// 清除所有存储
							uni.clearStorageSync();
							
							// 恢复登录状态和用户数据
							if (token) uni.setStorageSync('token', token);
							if (userInfo) uni.setStorageSync('currentUser', userInfo);
							
							// 重新加载设置
							this.loadSettings();
							// 重新计算缓存大小
							this.calculateCacheSize();
							
							uni.hideLoading();
							uni.showToast({
								title: '缓存已清除',
								icon: 'success'
							});
						}, 1000);
					}
				}
			});
		},
		
		// 跳转到关于页面
		goToAbout() {
			uni.navigateTo({
				url: '/pages/about/about'
			});
		},
		
		// 退出登录
		logout() {
			uni.showModal({
				title: '提示',
				content: '确定要退出登录吗？',
				success: (res) => {
					if (res.confirm) {
						// 清除登录信息
						uni.removeStorageSync('token');
						uni.removeStorageSync('currentUser');
						uni.removeStorageSync('savedLoginInfo');
						
						// 显示提示
						uni.showToast({
							title: '已退出登录',
							icon: 'success'
						});
						
						// 延迟后跳转到登录页
						setTimeout(() => {
							uni.reLaunch({
								url: '/pages/login/login'
							});
						}, 1500);
					}
				}
			});
		}
	}
}
</script>

<style>
.setting-container {
	display: flex;
	flex-direction: column;
	min-height: 100vh;
	background-color: #f5f5f5;
	padding-bottom: 40rpx;
}

.setting-list {
	margin-top: 20rpx;
}

.setting-group {
	background-color: #fff;
	margin-bottom: 20rpx;
}

.setting-group-title {
	padding: 20rpx 30rpx;
	font-size: 28rpx;
	color: #999;
	background-color: #f5f5f5;
}

.setting-item {
	display: flex;
	align-items: center;
	justify-content: space-between;
	padding: 30rpx;
	border-bottom: 1px solid #eee;
}

.setting-item:last-child {
	border-bottom: none;
}

.setting-label-container {
	display: flex;
	align-items: center;
}

.setting-label {
	font-size: 30rpx;
	color: #333;
	margin-left: 15rpx;
}

.setting-value-container {
	display: flex;
	align-items: center;
}

.setting-value {
	font-size: 28rpx;
	color: #999;
	margin-right: 10rpx;
}

.picker-value {
	font-size: 28rpx;
	color: #666;
	display: flex;
	align-items: center;
}

.version-info {
	text-align: center;
	padding: 40rpx 0;
	font-size: 24rpx;
	color: #999;
	margin-top: auto;
}

.logout-group {
	margin-top: 60rpx;
}

.logout-text {
	color: #ff4d4f;
	font-size: 32rpx;
	text-align: center;
	width: 100%;
}
</style>