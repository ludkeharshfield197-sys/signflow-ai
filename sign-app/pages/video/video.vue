<template>
	<view class="video-container">
		<!-- 页面标题 -->
		<view class="page-header">
			<text class="page-title">视频手语识别</text>
		</view>
		
		<!-- 上传区域 -->
		<view class="upload-area" @tap="chooseVideo">
			<view v-if="!videoUrl" class="upload-empty">
				<view class="upload-icon">
					<uni-icons type="videocam" size="30"></uni-icons>
				</view>
				<text class="upload-text">点击上传手语视频</text>
			</view>
			<video v-else class="preview-video" :src="videoUrl" controls></video>
		</view>
		
		<!-- 操作按钮 -->
		<view class="action-buttons">
			<button class="action-btn wide-btn" type="default" @tap="recognizeVideo" 
				:disabled="!videoUrl || isRecognizing" 
				:loading="isRecognizing">
				<uni-icons type="checkmarkempty" size="30"></uni-icons>
				<text class="btn-text">开始识别</text>
			</button>
		</view>
		
		<!-- 识别结果 -->
		<view v-if="resultVideoUrl || generatedSentence" class="result-section">
			<view class="result-header">
				<text class="section-title">识别结果</text>
			</view>
			
			<!-- 手语含义 - 改为显示生成的句子 -->
			<view v-if="generatedSentence" class="result-label">
				<text class="result-meaning">{{ generatedSentence }}</text>
			</view>
			
			<!-- 结果视频 -->
			<view v-if="resultVideoUrl" class="result-video-wrapper">
				<video class="result-video" :src="resultVideoUrl" controls></video>
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
			videoUrl: '', // 原始视频URL
			videoFile: null, // 视频文件对象
			resultVideoUrl: '', // 处理后的视频URL
			recognitionResult: null, // 识别结果
			generatedSentence: '', // 生成的句子
			isRecognizing: false, // 是否正在识别中
			baseUrl: getServerUrl(), // 服务器基础URL
			
			// 模型相关 - 使用固定模型ID
			selectedModel: {
				id: '37',  // 使用字符串类型的model_id，固定为29
				name: 'YOLOv8n'  // 显示名称
			},
			
			// 参数设置
			iouThreshold: 0.45,
			confidenceThreshold: 0.25,
			
			// 任务ID
			taskId: null
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
		
		// 选择视频
		chooseVideo() {
			uni.chooseVideo({
				count: 1,
				sourceType: ['album', 'camera'],
				maxDuration: 60, // 限制最大时长为60秒
				camera: 'back',
				success: (res) => {
					console.log('选择视频成功:', res);
					this.videoUrl = res.tempFilePath;
					this.videoFile = {
						path: res.tempFilePath,
						size: res.size,
						duration: res.duration,
						height: res.height,
						width: res.width
					};
					// 清空之前的识别结果
					this.resultVideoUrl = '';
					this.recognitionResult = null;
					this.generatedSentence = '';
					this.taskId = null;
				}
			});
		},
		
		// 识别视频
		recognizeVideo() {
			if (!this.videoUrl) {
				uni.showToast({
					title: '请先选择视频',
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
			
			// 显示加载提示
			uni.showLoading({
				title: '视频上传中...',
				mask: true
			});
			
			// 上传视频并进行识别
			uni.uploadFile({
				url: this.baseUrl + 'video/submit/',
				filePath: this.videoUrl,
				name: 'video',
				header: {
					'Authorization': token
				},
				formData: {
					'model_id': '36',  // 使用固定的模型ID
					'iou_threshold': this.iouThreshold,
					'confidence_threshold': this.confidenceThreshold
				},
				success: (res) => {
					try {
						console.log('服务器原始响应:', res.data);
						const response = JSON.parse(res.data);
						console.log('解析后响应:', response);
						
						if (response.code === 200) {
							// 保存任务ID
							this.taskId = response.data.task_id;
							
							// 显示处理中提示
							uni.showLoading({
								title: '视频处理中...',
								mask: true
							});
							
							// 开始轮询检查处理结果
							this.pollVideoResult();
						} else {
							// 上传失败
							uni.showToast({
								title: response.message || '上传失败',
								icon: 'none'
							});
							this.isRecognizing = false;
							uni.hideLoading();
						}
					} catch (error) {
						console.error('解析响应失败:', error);
						console.error('原始响应数据:', res.data);
						uni.showToast({
							title: '服务器响应格式错误',
							icon: 'none'
						});
						this.isRecognizing = false;
						uni.hideLoading();
					}
				},
				fail: (error) => {
					console.error('上传请求失败:', error);
					uni.showToast({
						title: '网络请求失败',
						icon: 'none'
					});
					this.isRecognizing = false;
					uni.hideLoading();
				}
			});
		},
		
		// 轮询视频处理结果
		pollVideoResult() {
			if (!this.taskId) {
				uni.hideLoading();
				this.isRecognizing = false;
				return;
			}
			
			// 使用detail接口获取视频详情
			request.get(`video/detail/${this.taskId}/`)
				.then(res => {
					console.log('获取视频详情:', res);
					
					if (res.code === 200) {
						// 检查是否有结果视频
						if (res.data.result_video) {
							// 处理完成，显示结果
							this.resultVideoUrl = res.data.result_video;
							
							// 获取生成的句子
							if (res.data.generated_sentence) {
								this.generatedSentence = res.data.generated_sentence;
							} else {
								// 如果没有句子，尝试获取句子
								this.fetchGeneratedSentence();
							}
							
							// 保留检测结果摘要用于调试
							if (res.data.detection_result_summary) {
								this.recognitionResult = res.data.detection_result_summary;
							} else if (res.data.detection_result) {
								// 如果没有摘要但有详细结果，则计算摘要
								const summary = {};
								for (const cls in res.data.detection_result) {
									summary[cls] = res.data.detection_result[cls].length;
								}
								this.recognitionResult = summary;
							} else {
								this.recognitionResult = { '未识别': 0 };
							}
							
							uni.hideLoading();
							uni.showToast({
								title: '识别成功',
								icon: 'success'
							});
							this.isRecognizing = false;
						} else if (res.data.status === 'failed') {
							// 处理失败
							uni.hideLoading();
							uni.showToast({
								title: res.data.error_message || '处理失败',
								icon: 'none'
							});
							this.isRecognizing = false;
						} else {
							// 继续等待，2秒后再次查询
							setTimeout(() => {
								this.pollVideoResult();
							}, 2000);
						}
					} else {
						// API错误
						uni.hideLoading();
						uni.showToast({
							title: res.message || '获取处理状态失败',
							icon: 'none'
						});
						this.isRecognizing = false;
					}
				})
				.catch(error => {
					console.error('获取视频详情失败:', error);
					
					// 如果是网络错误，可以继续尝试
					setTimeout(() => {
						this.pollVideoResult();
					}, 3000);
				});
		},
		
		// 新增方法：获取生成的句子
		fetchGeneratedSentence() {
			if (!this.taskId) {
				console.error('无法获取句子：任务ID为空');
				return;
			}
			
			console.log('开始获取生成的句子，任务ID:', this.taskId);
			uni.showLoading({ title: '生成结果中...' });
			
			// 添加重试逻辑
			let retryCount = 0;
			const maxRetries = 3;
			const retryInterval = 2000;
			
			const fetchSentence = () => {
				request.get(`video/sentence/?task_id=${this.taskId}`)
					.then(res => {
						uni.hideLoading();
						console.log('获取句子API响应:', JSON.stringify(res).substr(0, 200) + '...');
						
						if (res.code === 200 && res.data && res.data.sentence) {
							this.generatedSentence = res.data.sentence;
							console.log('成功获取生成句子:', this.generatedSentence);
							
							// 显示成功提示
							uni.showToast({
								title: '句子生成成功',
								icon: 'success'
							});
						} else if (res.code === 400 && res.message && 
								  (res.message.includes('正在处理') || 
								   res.message.includes('尚未处理完成') || 
								   res.message.includes('未找到'))) {
							// 结果正在处理中，需要重试
							if (retryCount < maxRetries) {
								retryCount++;
								console.log(`句子正在生成中，${retryInterval/1000}秒后第${retryCount}次重试...`);
								uni.showToast({
									title: '句子生成中...',
									icon: 'loading',
									duration: 1500
								});
								
								setTimeout(fetchSentence, retryInterval);
							} else {
								console.error('获取句子达到最大重试次数');
								this.generatedSentence = '句子生成超时，请稍后再试';
								uni.showToast({
									title: '句子生成超时',
									icon: 'none'
								});
							}
						} else {
							// 其他错误
							console.error('获取句子失败:', res.message);
							this.generatedSentence = res.message || '未能生成句子，请重试';
							uni.showToast({
								title: '生成句子失败',
								icon: 'none'
							});
						}
					})
					.catch(err => {
						uni.hideLoading();
						console.error('获取生成句子请求失败:', err);
						
						if (retryCount < maxRetries) {
							retryCount++;
							console.log(`获取句子请求失败，${retryInterval/1000}秒后第${retryCount}次重试...`);
							
							setTimeout(fetchSentence, retryInterval);
						} else {
							this.generatedSentence = '网络请求失败，请检查网络';
							uni.showToast({
								title: '网络请求失败',
								icon: 'none'
							});
						}
					});
			};
			
			// 开始获取句子
			fetchSentence();
		}
	}
}
</script>

<style lang="scss">
.video-container {
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

.upload-text {
	font-size: 28rpx;
	color: #999;
}

.preview-video {
	width: 100%;
	height: 100%;
	object-fit: contain;
}

.model-section {
	background-color: #fff;
	border-radius: 20rpx;
	padding: 20rpx;
	margin-bottom: 30rpx;
	box-shadow: 0 4rpx 10rpx rgba(0, 0, 0, 0.05);
}

.section-label {
	font-size: 28rpx;
	color: #666;
	margin-bottom: 10rpx;
	display: block;
}

.model-picker {
	height: 80rpx;
	border: 1rpx solid #eee;
	border-radius: 10rpx;
	display: flex;
	align-items: center;
	justify-content: space-between;
	padding: 0 20rpx;
	font-size: 28rpx;
	color: #333;
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

.btn-text {
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
	font-size: 28rpx;
	color: #333;
	line-height: 1.5;
}

.result-video-wrapper {
	margin-top: 20rpx;
}

.result-video {
	width: 100%;
	height: 400rpx;
	border-radius: 10rpx;
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
</style>
