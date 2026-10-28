<template>
	<view class="image-container">
		<!-- 页面标题 -->
		<view class="page-header">
			<text class="page-title">图片手语识别</text>
		</view>
		
		<!-- 上传区域 -->
		<view class="upload-area" @tap="chooseImage">
			<view v-if="!imageUrl" class="upload-empty">
				<view class="upload-icon">
					<uni-icons type="image" size="30"></uni-icons>
				</view>
				<text class="upload-text">点击上传手语图片</text>
			</view>
			<image v-else class="preview-image" :src="imageUrl" mode="aspectFit"></image>
		</view>
		
		<!-- 操作按钮 - 只保留识别按钮 -->
		<view class="action-buttons">
			<button class="action-btn wide-btn" type="default" @tap="recognizeImage" :disabled="!imageUrl || isRecognizing" :loading="isRecognizing">
				<uni-icons type="checkmarkempty" size="30"></uni-icons>
				
				<text class="btn-text">开始识别</text>
			</button>
		</view>
		
		<!-- 识别结果 -->
		<view v-if="processedImageUrl || recognitionResult" class="result-section">
			<view class="result-header">
				<text class="section-title">识别结果</text>
			</view>
			
			<!-- 手语含义 -->
			<view v-if="recognitionResult" class="result-label">
				<text class="result-meaning">{{ recognitionResult }}</text>
			</view>
			
			<!-- 结果图片 -->
			<view v-if="processedImageUrl" class="result-image-wrapper">
				<image class="result-image" :src="processedImageUrl" mode="aspectFit"></image>
			</view>
		</view>
	</view>
</template>

<script>
import request from '../../utils/request.js';
import { getServerUrl } from '../../utils/request.js';
export default {
	data() {
		return {
			imageUrl: '', // 原始图片URL
			imageFile: null, // 图片文件对象
			processedImageUrl: '', // 处理后的图片URL (带标记的)
			recognitionResult: '', // 识别结果
			isRecognizing: false, // 是否正在识别中
			baseUrl: getServerUrl() // 设置服务器基础URL
		}
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
					url: '/pages/login/login'
				});
			}
		},
		
		// 选择图片
		chooseImage() {
			uni.chooseImage({
				count: 1,
				sizeType: ['original', 'compressed'],
				sourceType: ['album', 'camera'],
				success: (res) => {
					this.imageUrl = res.tempFilePaths[0];
					this.imageFile = res.tempFiles[0];
					// 清空之前的识别结果
					this.processedImageUrl = '';
					this.recognitionResult = '';
				}
			});
		},
		
		// 识别图片
		recognizeImage() {
			if (!this.imageUrl) {
				uni.showToast({
					title: '请先选择图片',
					icon: 'none'
				});
				return;
			}
			
			// 获取token
			const token = uni.getStorageSync('token');
			if (!token) {
				uni.showToast({
					title: '请先登录',
					icon: 'none'
				});
				return;
			}
			
			this.isRecognizing = true;
			
			// 修改请求格式
			uni.uploadFile({
				url: this.baseUrl + '/image/detect/', 
				filePath: this.imageUrl,
				name: 'image', // 修改文件参数名为image
				header: {
					'Authorization': token
				}, 
				formData: {
					'model_id': '37' // 使用字符串类型的model_id
				},
				success: (res) => {
					try {
						console.log('服务器原始响应:', res.data);
						const response = JSON.parse(res.data);
						console.log('解析后响应:', response);
						
						if (response.code === 200) {
							// 处理返回的图片 - 支持两种格式：URL或Base64
							if (response.data.result_image && response.data.result_image.startsWith('data:image')) {
								// 如果是Base64格式的图片数据
								this.processedImageUrl = response.data.result_image;
							} else if (response.data.image_url) {
								// 如果是图片URL
								this.processedImageUrl = this.baseUrl + response.data.image_url;
							}
							
							// 识别结果处理
							if (Array.isArray(response.data.detections) && response.data.detections.length > 0) {
								// 获取第一个检测结果的class
								this.recognitionResult = response.data.detections[0].class || '未识别到任何手语';
							} else if (response.data.class) {
								this.recognitionResult = response.data.class;
							} else if (response.data.result) {
								this.recognitionResult = response.data.result;
							} else {
								this.recognitionResult = '未识别到任何手语';
							}
							this.recognitionResult = this.recognitionResult[0].class
							
							uni.showToast({
								title: '识别成功',
								icon: 'success'
							});
						} else {
							// 识别失败
							uni.showToast({
								title: response.message || '识别失败',
								icon: 'none'
							});
						}
					} catch (error) {
						console.error('解析响应失败:', error);
						console.error('原始响应数据:', res.data);
						uni.showToast({
							title: '服务器响应格式错误',
							icon: 'none'
						});
					}
				},
				fail: (error) => {
					console.error('上传请求失败:', error);
					uni.showToast({
						title: '网络请求失败',
						icon: 'none'
					});
				},
				complete: () => {
					this.isRecognizing = false;
				}
			});
		}
	}
}
</script>

<style lang="scss">
.image-container {
	padding: 30rpx;
	background-color: #f5f5f5;
	min-height: 100vh;
}

.page-header {
	margin-bottom: 30rpx;
}

.page-title {
	font-size: 36rpx;
	font-weight: bold;
	color: #333;
}

.upload-area {
	background-color: #fff;
	border-radius: 20rpx;
	height: 400rpx;
	display: flex;
	justify-content: center;
	align-items: center;
	margin-bottom: 30rpx;
	overflow: hidden;
	box-shadow: 0 4rpx 10rpx rgba(0, 0, 0, 0.05);
}

.upload-empty {
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	width: 100%;
	height: 100%;
}

.upload-icon {
	font-size: 80rpx;
	color: #ddd;
	margin-bottom: 20rpx;
	display: flex;
	align-items: center;
	justify-content: center;
}

.upload-icon .iconfont {
	font-size: 80rpx;
}

.upload-text {
	font-size: 28rpx;
	color: #999;
}

.preview-image {
	width: 100%;
	height: 100%;
	object-fit: contain;
}

.action-buttons {
	margin-bottom: 30rpx;
}

.action-btn {
	display: flex;
	flex-direction: row;
	align-items: center;
	justify-content: center;
}

.wide-btn {
	width: 100% !important;
}

.action-btn .iconfont {
	margin-right: 10rpx;
	color: inherit;
}

.action-btn .btn-text {
	font-size: 28rpx;
}

.result-section {
	background-color: #fff;
	border-radius: 20rpx;
	box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.1);
	padding: 30rpx;
	margin-top: 20rpx;
}

.result-header {
	border-bottom: 1px solid #eee;
	padding-bottom: 20rpx;
	margin-bottom: 20rpx;
}

.section-title {
	font-size: 32rpx;
	font-weight: bold;
	color: #333;
}

.result-label {
	background-color: #f8f8f8;
	border-radius: 10rpx;
	padding: 20rpx;
	margin-bottom: 20rpx;
	text-align: center;
}

.result-meaning {
	font-size: 36rpx;
	font-weight: bold;
	color: #333;
}

.result-image-wrapper {
	margin-top: 20rpx;
}

.result-image {
	width: 100%;
	height: 400rpx;
	border-radius: 10rpx;
	object-fit: contain;
}

/* 图标字体 */
@font-face {
	font-family: 'iconfont';
	src: url('data:application/x-font-woff2;charset=utf-8;base64,d09GMgABAAAAAAVgAAsAAAAACiQAAAUTAAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHEIGVgCDMgqHTIY+ATYCJAMUCwwABCAFhG0HUBumCFGUTk6Y7AsJzuVoEXVmTQy1mJ6c4uaaNtHw//X7/b+5M+99ImEaTERJRZKJRFpEgkgUS4msTdTm+3fN1wsSNinlWrb80tSAUjxANxU4v1ZrGI6rTVFhqE3G/3M4adXC8tvZXDIyGoXjQQc01mYLkh3oHfCdCfh/PE11BheTQLdJgQhHqusrQK6QRgXiISW1ArlqlIowhjZUe1YW8RU0NZ/SJ8CX4P3xH4jiQtIU0ujoXSNDoOpn5bmU7//XSpkFxO15YLeTsMAGYBHP+lpPSzG8wUK3+RneAzRNktpMz6We65/L/1/q5QIhzZAxGmn0Hy8lK6JGmngTHcvPE05IfiZ8goRUz04qQh3jRrjPnJMRGqVLGxXgDeAFMRpj/Ih0GZOMKKfXRqx/m7YfjC1dGNu+mhRJkyPrFmC9I3vSRFe6Oll/6UpnzeSZk/Qdrk7WnLSLzs5M1L0aYjQWjxXpW5Wdnr55/XopVLpnzRp1/XrPGk/d7Fm7NnHq7IWJC3RKRVqiblzqpCnTRVDXZbYw5zypmDTD0LV16hY9qUucsXb93rXBdTfC9CKKF2lCXdfpstLEXBPqrp9I4JKFi7eQXbBwaSmPmLXTQHPOjdFFFCXOn72w5Uoie34JRUk7jCcjdFPeS3i9MpGgRO1qTQwUzVqkpSYmTN26cd3J3fv2Hdi3a2/vxBQh0W7/lXV+7dr5a/bHmOO2hO2LO6cNb8scFa/beaW/tKyopNJr1o86/Y03jj/Z2FWXGkrQz6hduxJ01u1E9mA1pYqUKttR68B8bpYlR2Kp+aT2a8/CYMq5m7G5b4wc4Tp65Ax//Rr1+vWqRazCXmIviPsjdtrLwdVuD2nJ7YEAewq/1Pw28VbCamlLUmkSVSkbVyabAknsz7fvHWbqyZ52cI0O+zY2Ws3b163Z36DBG4vafOjEiaGvvNKp+/yLXdxeeXVpp7d62cK4kc4u//xVrxGtu7/3XndSCz+1J1oQdIa4PEd8dCTpkMstSNJRQh6/VGCRw6OYMK5e2b1Hp06xVw/U+5eoZ0yYyAvNjZT6D/7cHVMT9+v4+ONyuLEsC41pMaFXZw2bMUMQNe5O0eNNR/z+Tx1Yxvmya/f33uvuxjYUL7+QjcwZa9nvP08dSEb9GRWKXQzZaRn1k/k1JlbvtKWOzPeZVhxtktBqYOPBdcSj7Wb3Y/jFB40p1y5Z0vbEoKpbP2pEvrCO+cSIj88nqz4qF9KD7/j4Mx1HaQlFGxmMnK28ksVqxYWczT4hCLUZ2fF33/r76+/lIlNqIxQl/H8UsjoBfJMuhJ7Rv9r7BTT3G1ocPO2/TrpHq6T/qVcWBv3b0uWiVp0zVRbrmtw73Kg+Ip5Apc+QPg58J+qdoxtW/eCItklImlYgaxeTFmMDNT3WoNK2Bt2W1RzuMYZ5kYp2WLWDEHrdQ9LpO3K97kkL8S1qRv1ApTcM6HYUxBP2mANThAarU9SCHOTzKoLNDCRpnMbRE+okCkIZJQ6HQo1Y8W0xDiOGqMOezTpJPT8vA9YuI2f6kGBWo9UbHMZzx9iiiFWrzCsJUzxCcQEzQ6hANeRUyAtykM5TImDTzEOkMR2d9wR1RKL3pSjiNlXQuNrC6Vk7whA1Q3ow2exEyieSMWy1l5lR3y8BmJlFVl2Dv5+b+7aQktRUWqPSIku8UoP1quoZAICuxh2CEkopNTQyhgUtTnMRQ5Yj9c3rpTiJKlHmlWTpZM4AAAAA') format('woff2');
}

.iconfont {
	font-family: "iconfont" !important;
	font-size: 32rpx;
	font-style: normal;
	-webkit-font-smoothing: antialiased;
	-moz-osx-font-smoothing: grayscale;
	color: #999;
}

.icon-camera:before {
	content: "\e6ac";
}

.icon-picture:before {
	content: "\e6bd";
}

.icon-search:before {
	content: "\e67d";
}
</style>