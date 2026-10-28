<template>
	<view class="camera-container">
		<!-- 页面标题 -->
		<view class="page-header">
			<text class="page-title">摄像头手语识别</text>
		</view>
		
		<!-- 摄像头区域 - 始终显示，不管是否在识别 -->
		<view class="camera-area">
			<camera v-if="isCameraOpen" :device-position="devicePosition" flash="off" @error="handleCameraError" class="camera"></camera>
			<canvas v-if="isCameraOpen" canvas-id="previewCanvas" class="preview-canvas"></canvas>
			<view v-if="!isCameraOpen" class="camera-closed">
				<view class="camera-icon">
					<uni-icons type="videocam" size="30"></uni-icons>
				</view>
				<text class="camera-text">点击"开始识别"按钮开启摄像头</text>
			</view>
		</view>
		
		<!-- 当前识别类别（仅在识别过程中显示） -->
		<view v-if="isRecognizing && currentDetections.length > 0" class="detection-box">
			<view class="detection-title">当前识别：</view>
			<view class="detection-labels">
				<view v-for="(detection, index) in currentDetections" :key="index" class="detection-item">
					<text class="detection-class">{{detection.class}}</text>
					<text class="detection-confidence">{{(detection.confidence * 100).toFixed(0)}}%</text>
				</view>
			</view>
		</view>
		
		<!-- 操作按钮 -->
		<view class="action-buttons">
			<button v-if="!isRecognizing" class="action-btn primary-btn" @tap="startRecognition" :disabled="isProcessing">
				<text class="btn-text">开始识别</text>
			</button>
			<button v-else class="action-btn stop-btn" @tap="stopRecognition" :disabled="isProcessing">
				<text class="btn-text">停止识别</text>
			</button>
			<button v-if="isCameraOpen" class="action-btn secondary-btn" @tap="switchCamera" :disabled="isProcessing">
				<text class="btn-text">切换摄像头</text>
			</button>
		</view>
		
		<!-- 检测结果统计（仅在停止识别后有结果时显示） -->
		<view v-if="!isRecognizing && detectionSummary.length > 0" class="result-section">
			<view class="section-title">检测结果统计</view>
			<view class="result-table">
				<view class="table-header">
					<view class="table-cell class-cell">类别</view>
					<view class="table-cell count-cell">次数</view>
					<view class="table-cell conf-cell">平均置信度</view>
				</view>
				<view class="table-body">
					<view class="table-row" v-for="(item, index) in detectionSummary" :key="index">
						<view class="table-cell class-cell">{{item.class}}</view>
						<view class="table-cell count-cell">{{item.count}}</view>
						<view class="table-cell conf-cell" v-if="item.avgConfidence">{{item.avgConfidence}}%</view>
						<view class="table-cell conf-cell" v-else>-</view>
					</view>
				</view>
			</view>
		</view>
		
		<!-- 生成的句子显示（仅在停止识别后有句子时显示） -->
		<view v-if="!isRecognizing && generatedSentence" class="sentence-box">
			<view class="sentence-title">生成句子：</view>
			<view class="sentence-content">
				<text>{{generatedSentence}}</text>
			</view>
		</view>
		
		<!-- 底部区域占位 -->
		<view style="height: 30rpx;"></view>
	</view>
</template>

<script>
import request from '../../utils/request.js';
import { getServerUrl, getWebSocketUrl } from '../../utils/request.js';

export default {
	data() {
		return {
			isCameraOpen: false,
			isRecognizing: false,
			isProcessing: false,
			devicePosition: 'back', // 摄像头朝向，默认后置
			
			// 会话相关
			sessionId: '',
			wsConnection: null,
			captureInterval: null,
			
			// 识别结果
			currentDetections: [], // 当前帧的检测结果
			allDetections: {}, // 累计的检测结果 {类别: 次数}
			detectionSummary: [], // 检测结果统计 [{class: '类别', count: 次数}]
			generatedSentence: '', // 生成的句子
			
			// 服务器URL
			baseUrl: getServerUrl(),
			wsBaseUrl: getWebSocketUrl(),
			
			// 固定模型ID - 使用字符串类型，确保与后端匹配
			modelId: '37',
			
			// 参数设置
			iouThreshold: 0.30,
			confidenceThreshold: 0.30,
			
			// 摄像头上下文
			cameraContext: null,
			
			// 帧率控制
			lastCaptureTime: 0,
			frameCaptureInterval: 200, // 捕获间隔，毫秒
			
			// 心跳相关
			heartbeatInterval: null,
			
			// 图像错误相关
			imageErrorCount: 0,
			
			// 连接错误相关
			connectRetryCount: 0,
			maxConnectRetries: 3, // 最大重试次数
			isAppActive: true, // 跟踪应用是否在前台
			
			// 结果超时相关
			resultTimeout: null,
			
			stopMsgConfirmed: false
		}
	},
	onLoad() {
		// 检查登录状态
		this.checkLoginStatus();
	},
	onShow() {
		// 页面显示时标记为活跃
		this.isAppActive = true;
		
		// 如果处于识别状态，尝试恢复连接
		if (this.isRecognizing && !this.wsConnection) {
			console.log('页面重新显示，尝试恢复连接');
			this.connectWebSocket();
		}
	},
	onHide() {
		// 页面隐藏时标记为非活跃
		this.isAppActive = false;
		
		// 如果连接仍然活跃，暂停图像捕获以节省资源
		if (this.captureInterval) {
			clearInterval(this.captureInterval);
			this.captureInterval = null;
			console.log('页面隐藏，暂停图像捕获');
		}
	},
	onUnload() {
		console.log('页面即将卸载，关闭资源');
		
		// 停止所有定时器
		if (this.captureInterval) {
			clearInterval(this.captureInterval);
			this.captureInterval = null;
		}
		
		if (this.heartbeatInterval) {
			clearInterval(this.heartbeatInterval);
			this.heartbeatInterval = null;
		}
		
		if (this.resultTimeout) {
			clearTimeout(this.resultTimeout);
			this.resultTimeout = null;
		}
		
		// 如果还在识别中，先停止识别
		if (this.isRecognizing) {
			this.isRecognizing = false;
			
			// 尝试发送停止消息，但不等待结果
			if (this.wsConnection) {
				this.sendWebSocketMessage({
					type: 'stop_detection',
					session_id: this.sessionId,
					force_close: true // 告诉服务器强制关闭
				});
			}
		}
		
		// 关闭WebSocket连接
		if (this.wsConnection) {
			console.log('关闭WebSocket连接');
			
			try {
				// 通知服务器客户端即将关闭
				this.sendWebSocketMessage({
					type: 'client_closing',
					session_id: this.sessionId
				});
				
				// 延迟1秒再关闭，给服务器处理时间
				setTimeout(() => {
					try {
						this.wsConnection.close();
					} catch (e) {
						console.error('关闭WebSocket连接异常:', e);
					} finally {
						this.wsConnection = null;
					}
				}, 1000);
			} catch (e) {
				console.error('关闭前发送消息异常:', e);
				try {
					this.wsConnection.close();
				} catch (e2) {
					console.error('关闭WebSocket连接异常:', e2);
				} finally {
					this.wsConnection = null;
				}
			}
		}
		
		// 关闭摄像头
		this.isCameraOpen = false;
		this.cameraContext = null;
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
		
		// 处理摄像头错误
		handleCameraError(e) {
			console.error('摄像头错误:', e);
			uni.showToast({
				title: '摄像头启动失败',
				icon: 'none'
			});
			this.isCameraOpen = false;
			this.isRecognizing = false;
		},
		
		// 开始识别
		startRecognition() {
			// 先关闭之前可能存在的连接
			if (this.wsConnection) {
				this.closeConnection();
			}
			
			this.isProcessing = true;
			// 清除之前的结果
			this.currentDetections = [];
			this.allDetections = {};
			this.detectionSummary = [];
			this.generatedSentence = '';
			
			// 初始化会话
			uni.showLoading({ title: '初始化中...' });
			
			// 修正API路径，从CameraModel/init/改为camera/init/
			request.post('camera/init/', {
				model_id: this.modelId,
				iou_threshold: this.iouThreshold,
				confidence_threshold: this.confidenceThreshold
			}).then(res => {
				if (res.code === 200 && res.data && res.data.session_id) {
					this.sessionId = res.data.session_id;
					console.log('会话初始化成功，ID:', this.sessionId);
					
					// 打开摄像头
					this.isCameraOpen = true;
					// 初始化摄像头上下文
					this.cameraContext = uni.createCameraContext();
					
					// 建立WebSocket连接
					this.connectWebSocket();
				} else {
					uni.showToast({
						title: res.message || '初始化失败',
						icon: 'none'
					});
					this.isProcessing = false;
				}
				uni.hideLoading();
			}).catch(err => {
				console.error('初始化会话失败:', err);
				uni.showToast({
					title: '网络请求失败',
					icon: 'none'
				});
				this.isProcessing = false;
				uni.hideLoading();
			});
		},
		
		// 连接WebSocket
		connectWebSocket() {
			if (!this.sessionId) {
				uni.showToast({
					title: '会话ID无效',
					icon: 'none'
				});
				this.isProcessing = false;
				return;
			}
			
			// 关闭所有连接，解决"exceed max task count"错误
			try {
				// 先尝试关闭当前连接
				if (this.wsConnection) {
					try {
						this.wsConnection.close({
							success: () => {
								console.log('成功关闭旧连接');
							}
						});
					} catch (error) {
						console.error('关闭旧连接失败:', error);
					}
					this.wsConnection = null;
				}
				
				// 尝试关闭所有WebSocket连接
				uni.closeSocket({
					success: () => {
						console.log('成功关闭全局WebSocket连接');
					},
					fail: () => {
						console.log('没有需要关闭的全局WebSocket连接');
					}
				});
			} catch (e) {
				console.error('清理WebSocket连接出错:', e);
			}
			
			// 等待一小段时间再建立新连接
			setTimeout(() => {
				// 确保WebSocket路径与routing.py匹配
				const wsUrl = `${this.wsBaseUrl}ws/camera/${this.sessionId}/`;
				console.log('尝试连接WebSocket:', wsUrl);
				
				try {
					// 使用SocketTask方式建立连接，避免小程序环境中的冲突
					this.wsConnection = uni.connectSocket({
						url: wsUrl,
						header: {
							'content-type': 'application/json',
							'Authorization': uni.getStorageSync('token') || '' // 添加token验证
						},
						success: () => {
							console.log('WebSocket连接请求已发送');
						},
						fail: (err) => {
							console.error('WebSocket连接请求失败:', err);
							
							if (err.errMsg === "exceed max task count") {
								// 连接数量超限，提示用户关闭其他页面或重启小程序
								uni.showModal({
									title: 'WebSocket连接受限',
									content: '请关闭其他页面或重启小程序后再试',
									showCancel: false,
									success: () => {
										this.isProcessing = false;
										this.isCameraOpen = false;
									}
								});
							} else {
								uni.showToast({
									title: 'WebSocket连接失败',
									icon: 'none'
								});
								this.isProcessing = false;
								this.isCameraOpen = false;
							}
						}
					});
					
					// 使用SocketTask对象监听事件，而不是全局事件
					if (this.wsConnection) {
						this.wsConnection.onOpen(() => {
							console.log('WebSocket连接已打开');
							this.isRecognizing = true;
							this.isProcessing = false;
							
							// 开始定时捕获图像
							this.startCapture();
							
							// 发送心跳
							this.startHeartbeat();
						});
						
						this.wsConnection.onError((res) => {
							console.error('WebSocket错误:', res);
							uni.showToast({
								title: 'WebSocket连接错误',
								icon: 'none'
							});
							this.closeConnection();
						});
						
						this.wsConnection.onMessage((res) => {
							try {
								const data = JSON.parse(res.data);
								this.handleSocketMessage(data);
							} catch (e) {
								console.error('解析WebSocket消息失败:', e);
							}
						});
						
						this.wsConnection.onClose(() => {
							console.log('WebSocket连接已关闭');
							this.wsConnection = null;
							
							// 如果是正在识别中被关闭，显示提示
							if (this.isRecognizing) {
								uni.showToast({
									title: 'WebSocket连接已断开',
									icon: 'none'
								});
								this.stopRecognition(true); // 不发送结束消息
							}
						});
					} else {
						console.error('WebSocket对象创建失败');
						this.isProcessing = false;
						this.isCameraOpen = false;
						uni.showToast({
							title: 'WebSocket创建失败',
							icon: 'none'
						});
					}
				} catch (err) {
					console.error('创建WebSocket时发生异常:', err);
					this.isProcessing = false;
					this.isCameraOpen = false;
					uni.showToast({
						title: 'WebSocket创建异常',
						icon: 'none'
					});
				}
			}, 500); // 延迟500ms再建立连接，确保旧连接已完全关闭
		},
		
		// 处理WebSocket消息
		handleSocketMessage(data) {
			// 输出完整的消息内容，帮助调试
			console.log('收到WebSocket消息:', JSON.stringify(data).substr(0, 200) + '...');
			
			// 清除可能存在的超时定时器
			if (this.resultTimeout) {
				clearTimeout(this.resultTimeout);
				this.resultTimeout = null;
				console.log('已清除结果超时定时器');
			}
			
			// 处理服务器返回的各类消息
			switch(data.type) {
				case 'detection_result':
					// 处理检测结果
					if (data.result && data.result.detections) {
						// 更新当前帧的检测结果
						this.currentDetections = data.result.detections;
						
						// 累计检测结果
						this.updateDetectionStats(data.result.detections);
					}
					break;
					
				case 'detection_completed':
					console.log('收到检测完成消息，服务器已保存结果');
					
					// 隐藏加载提示
					uni.hideLoading();
					
					// 处理服务器返回的摘要数据
					if (data.summary && Array.isArray(data.summary)) {
						// 保存服务器返回的摘要数据
						this.detectionSummary = [...data.summary];
						
						// 按检测次数降序排序
						this.detectionSummary.sort((a, b) => b.count - a.count);
						console.log('已更新检测摘要数据:', this.detectionSummary.length, '条');
						
						// 显示结果已获取的提示
						uni.showToast({
							title: '识别完成',
							icon: 'success'
						});
					} else {
						console.warn('服务器未返回摘要数据，使用本地数据');
						// 使用本地累计的数据
						this.generateDetectionSummary();
					}
					
					// 设置为非处理状态
					this.isProcessing = false;
					
					// 获取生成的句子，不关闭连接
					this.fetchGeneratedSentence(false);
					
					// 不要在这里关闭连接！让连接保持打开状态直到离开页面
					break;
					
				case 'error':
					uni.hideLoading(); // 隐藏加载提示
					console.error('WebSocket错误消息:', data.message);
					
					this.isProcessing = false;
					
					// 错误情况下也使用本地数据
					this.generateDetectionSummary();
					
					// 获取句子但不关闭连接
					this.fetchGeneratedSentence(false);
					break;
					
				case 'cleanup_completed':
					console.log('清理完成:', data.message);
					this.isProcessing = false;
					break;
					
				case 'pong':
					console.log('收到心跳响应');
					break;
					
				case 'warning':
					uni.hideLoading(); // 隐藏加载提示
					console.warn('服务器警告:', data.message);
					uni.showToast({
						title: data.message,
						icon: 'none'
					});
					
					// 如果是会话到达最大时长限制的警告，主动停止识别
					if (data.message && data.message.includes('最大时长限制')) {
						this.stopRecognition(true);
					}
					
					this.isProcessing = false;
					break;
					
				default:
					console.log('未处理的消息类型:', data.type);
			}
		},
		
		// 累计检测结果统计
		updateDetectionStats(detections) {
			if (!detections || !Array.isArray(detections)) return;
			
			detections.forEach(detection => {
				const className = detection.class;
				if (className) {
					if (!this.allDetections[className]) {
						this.allDetections[className] = 0;
					}
					this.allDetections[className]++;
				}
			});
		},
		
		// 生成检测结果统计
		generateDetectionSummary() {
			// 根据累计的数据生成摘要
			this.detectionSummary = Object.entries(this.allDetections).map(([className, count]) => ({
				class: className,
				count: count,
				avgConfidence: 0 // 本地统计没有置信度平均值
			}));
			
			// 按检测次数降序排序
			this.detectionSummary.sort((a, b) => b.count - a.count);
		},
		
		// 开始捕获图像
		startCapture() {
			// 清除可能存在的旧定时器
			if (this.captureInterval) {
				clearInterval(this.captureInterval);
			}
			
			// 设置定时捕获
			this.captureInterval = setInterval(() => {
				if (this.isRecognizing && this.cameraContext) {
					const now = Date.now();
					// 控制帧率，避免发送过快
					if (now - this.lastCaptureTime >= this.frameCaptureInterval) {
						this.captureAndSend();
						this.lastCaptureTime = now;
					}
				}
			}, this.frameCaptureInterval);
		},
		
		// 捕获并发送图像
		captureAndSend() {
			if (!this.cameraContext || !this.isRecognizing) {
				return;
			}
			
			// 使用takePicture在较新的基础库中捕获图像 (不同版本兼容)
			if (this.cameraContext.takePicture) {
				this.cameraContext.takePicture({
					quality: 'low', // 降低质量以提高性能
					success: (res) => {
						// 读取图片并转换为base64
						this.convertImageToBase64(res.tempImagePath);
					},
					fail: (err) => {
						console.error('捕获图像失败:', err);
					}
				});
			} else {
				// 兼容旧版本，使用takePhoto
				this.cameraContext.takePhoto({
					quality: 'low',
					success: (res) => {
						this.convertImageToBase64(res.tempImagePath);
					},
					fail: (err) => {
						console.error('捕获图像失败:', err);
					}
				});
			}
		},
		
		// 将图像转换为Base64并发送
		convertImageToBase64(tempFilePath) {
			uni.getFileSystemManager().readFile({
				filePath: tempFilePath,
				encoding: 'base64',
				success: (res) => {
					// 发送图像数据，确保base64格式与consumers.py中的处理逻辑匹配
					// consumers.py期望收到'data:image/jpeg;base64,'格式的前缀
					const frameData = {
						type: 'frame',
						data: 'data:image/jpeg;base64,' + res.data
					};
					
					// 检查连接状态后发送
					if (this.wsConnection && this.isRecognizing) {
						this.sendWebSocketMessage(frameData);
					}
				},
				fail: (err) => {
					console.error('读取图像失败:', err);
					this.imageErrorCount++;
					// 错误计数超过阈值时考虑停止捕获
					if (this.imageErrorCount > 5) {
						console.error('连续读取图像失败，停止捕获');
						this.stopRecognition(true);
						uni.showToast({
							title: '摄像头异常，请重试',
							icon: 'none'
						});
					}
				}
			});
		},
		
		// 发送WebSocket消息
		sendWebSocketMessage(data) {
			if (!this.wsConnection) {
				console.error('WebSocket连接不存在，无法发送消息');
				return false;
			}
			
			try {
				// 如果是stop_detection消息，确保包含会话ID
				if (data.type === 'stop_detection' && !data.session_id) {
					data.session_id = this.sessionId;
				}
				
				console.log(`准备发送消息:`, JSON.stringify(data).substr(0, 200) + '...');
				
				// 使用SocketTask的send方法发送消息
				this.wsConnection.send({
					data: JSON.stringify(data),
					success: () => {
						console.log(`成功发送${data.type}消息`);
						return true;
					},
					fail: (err) => {
						console.error(`发送${data.type}消息失败:`, err);
						
						// 如果是重要消息，尝试重发
						if (data.type === 'stop_detection') {
							console.log('将在1秒后重试发送stop_detection消息');
							setTimeout(() => {
								console.log('重试发送stop_detection消息');
								this.sendWebSocketMessage(data);
							}, 1000);
						}
						
						return false;
					}
				});
				
				return true;
			} catch (error) {
				console.error(`发送${data.type}消息异常:`, error);
				return false;
			}
		},
		
		// 开始心跳
		startHeartbeat() {
			// 每30秒发送一次心跳
			this.heartbeatInterval = setInterval(() => {
				if (this.wsConnection) {
					this.sendWebSocketMessage({ type: 'ping' });
				}
			}, 30000);
		},
		
		// 完全重写stopRecognition方法
		async stopRecognition() {
			console.log('停止识别方法被调用');
			this.isRecognizing = false;
			
			// 清除捕获定时器
			if (this.captureInterval) {
				clearInterval(this.captureInterval);
				this.captureInterval = null;
				console.log('已清除图像捕获定时器');
			}
			
			// 检查WebSocket连接
			if (!this.wsConnection) {
				console.warn('WebSocket连接不存在，无法发送停止信号');
				return;
			}
			
			try {
				console.log('正在发送停止检测信号...');
				// 使用标准格式发送停止检测消息
				const stopMsg = {
					type: 'stop_detection',
					session_id: this.sessionId,
					message: 'stop detection and save results',
					timestamp: new Date().getTime()
				};
				
				// 使用统一的发送方法
				const sent = this.sendWebSocketMessage(stopMsg);
				
				if (sent) {
					console.log('成功发送停止检测信号');
					
					// 显示加载提示
					uni.showLoading({
						title: '正在保存结果...',
						mask: true
					});
					
					// 给后端足够时间处理和保存结果
					await new Promise(resolve => setTimeout(resolve, 5000));
					
					console.log('等待保存结果完成');
					uni.hideLoading();
					
					// 发送第二个确认消息，确保后端收到
					const confirmMsg = {
						type: 'confirm_stop',
						session_id: this.sessionId,
						message: 'confirm stop and save results',
						timestamp: new Date().getTime()
					};
					
					this.sendWebSocketMessage(confirmMsg);
					
					// 不关闭连接，继续等待结果
					console.log('停止检测流程完成，等待结果...');
				} else {
					console.error('停止检测信号发送失败');
					// 显示提示信息
					uni.showToast({
						title: '停止识别信号发送失败',
						icon: 'none'
					});
				}
			} catch (error) {
				console.error('发送停止检测信号时出错:', error);
			}
		},
		
		// 切换摄像头
		switchCamera() {
			this.devicePosition = this.devicePosition === 'back' ? 'front' : 'back';
		},
		
		// 获取生成的句子
		fetchGeneratedSentence(closeAfterFetch = false) {
			if (!this.sessionId) {
				console.error('无法获取句子：会话ID为空');
				return;
			}
			
			console.log('开始获取生成的句子，会话ID:', this.sessionId);
			uni.showLoading({ title: '生成结果中...' });
			
			// 添加重试逻辑
			let retryCount = 0;
			const maxRetries = 5; // 增加重试次数
			const retryInterval = 3000; // 增加重试间隔到3秒
			
			const fetchSentence = () => {
				request.get(`camera/sentence/?session_id=${this.sessionId}`)
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
							
							// 即使成功获取句子，也不关闭WebSocket连接
							// 让连接保持打开状态直到离开页面
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
		},
		
		// 重连WebSocket
		retryWebSocketConnection() {
			if (this.connectRetryCount >= this.maxConnectRetries || !this.isAppActive) {
				// 超过最大重试次数或应用不在前台，停止重试
				console.log('放弃WebSocket重连: 重试次数=', this.connectRetryCount, '应用活跃=', this.isAppActive);
				this.isProcessing = false;
				return;
			}
			
			this.connectRetryCount++;
			console.log(`尝试WebSocket重连 (${this.connectRetryCount}/${this.maxConnectRetries})...`);
			
			// 延迟重试，每次增加延迟
			setTimeout(() => {
				if (this.isAppActive) {
					this.connectWebSocket();
				}
			}, 1000 * this.connectRetryCount); // 递增延迟
		},
		
		// 关闭连接
		closeConnection() {
			// 这个方法在之前的版本中被多处调用
			// 我们保留它但不执行实际的关闭操作，以免干扰WebSocket通信
			console.log('closeConnection方法被调用，但我们现在不主动关闭WebSocket');
			
			// 清除定时器
			if (this.captureInterval) {
				clearInterval(this.captureInterval);
				this.captureInterval = null;
			}
			
			if (this.heartbeatInterval) {
				clearInterval(this.heartbeatInterval);
				this.heartbeatInterval = null;
			}
			
			if (this.resultTimeout) {
				clearTimeout(this.resultTimeout);
				this.resultTimeout = null;
			}
			
			// 重置状态
			this.isRecognizing = false;
			this.isProcessing = false;
			
			// 不关闭WebSocket连接！
			// 不关闭摄像头！
		}
	}
}
</script>

<style lang="scss">
.camera-container {
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

.camera-area {
	background-color: #fff;
	border-radius: 20rpx;
	height: 600rpx;
	position: relative;
	overflow: hidden;
	box-shadow: 0 4rpx 10rpx rgba(0, 0, 0, 0.05);
	margin-bottom: 30rpx;
}

.camera {
	width: 100%;
	height: 100%;
}

.preview-canvas {
	position: absolute;
	top: 0;
	left: 0;
	width: 100%;
	height: 100%;
	z-index: 10;
}

.camera-closed {
	width: 100%;
	height: 100%;
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
}

.camera-icon {
	font-size: 80rpx;
	color: #ddd;
	margin-bottom: 20rpx;
	display: flex;
	align-items: center;
	justify-content: center;
}

.camera-text {
	font-size: 28rpx;
	color: #999;
}

.detection-box {
	background-color: #fff;
	border-radius: 20rpx;
	padding: 20rpx;
	margin-bottom: 30rpx;
	box-shadow: 0 4rpx 10rpx rgba(0, 0, 0, 0.05);
}

.detection-title {
	font-size: 28rpx;
	font-weight: bold;
	color: #333;
	margin-bottom: 10rpx;
}

.detection-labels {
	display: flex;
	flex-wrap: wrap;
}

.detection-item {
	background-color: #f0f0f0;
	border-radius: 10rpx;
	padding: 10rpx 20rpx;
	margin-right: 20rpx;
	margin-bottom: 10rpx;
	display: flex;
	align-items: center;
}

.detection-class {
	color: #333;
	font-size: 26rpx;
	margin-right: 10rpx;
}

.detection-confidence {
	color: #999;
	font-size: 22rpx;
}

/* 检测结果统计样式 */
.result-section {
	background-color: #fff;
	border-radius: 20rpx;
	padding: 20rpx;
	margin-bottom: 30rpx;
	box-shadow: 0 4rpx 10rpx rgba(0, 0, 0, 0.05);
}

.section-title {
	font-size: 30rpx;
	font-weight: bold;
	color: #333;
	margin-bottom: 20rpx;
	padding-bottom: 10rpx;
	border-bottom: 1px solid #eee;
}

.result-table {
	width: 100%;
	border-radius: 10rpx;
	overflow: hidden;
	background-color: #fff;
}

.table-header {
	display: flex;
	background-color: #f5f5f5;
	font-weight: bold;
	font-size: 26rpx;
	color: #333;
	border-bottom: 1px solid #eee;
}

.table-body {
	max-height: 350rpx;
	overflow-y: auto;
}

.table-row {
	display: flex;
	border-bottom: 1px solid #f5f5f5;
	font-size: 26rpx;
	color: #333;
}

.table-row:last-child {
	border-bottom: none;
}

.table-cell {
	padding: 15rpx 10rpx;
	display: flex;
	align-items: center;
}

.class-cell {
	flex: 2;
	font-weight: bold;
}

.count-cell {
	flex: 1;
	justify-content: center;
	color: #007aff;
}

.conf-cell {
	flex: 1;
	justify-content: center;
	color: #666;
}

.sentence-box {
	background-color: #fff;
	border-radius: 20rpx;
	padding: 20rpx;
	margin-bottom: 30rpx;
	box-shadow: 0 4rpx 10rpx rgba(0, 0, 0, 0.05);
}

.sentence-title {
	font-size: 30rpx;
	font-weight: bold;
	color: #333;
	margin-bottom: 20rpx;
	padding-bottom: 10rpx;
	border-bottom: 1px solid #eee;
}

.sentence-content {
	padding: 20rpx;
	background-color: #f9f9f9;
	border-radius: 10rpx;
	color: #333;
	font-size: 28rpx;
	line-height: 1.5;
}

.action-buttons {
	display: flex;
	flex-direction: row;
	justify-content: space-between;
	margin-bottom: 30rpx;
}

.action-btn {
	flex: 1;
	margin: 0 10rpx;
	display: flex;
	flex-direction: row;
	align-items: center;
	justify-content: center;
	height: 80rpx;
	border-radius: 10rpx;
}

.primary-btn {
	background-color: #007aff;
	color: #fff;
}

.stop-btn {
	background-color: #ff3b30;
	color: #fff;
}

.secondary-btn {
	background-color: #f2f2f2;
	color: #333;
}

.btn-text {
	font-size: 28rpx;
}
</style>


