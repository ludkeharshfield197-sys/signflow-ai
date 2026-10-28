<script>
import { renewSession } from './services/request'
import { hasRefreshToken } from './services/session'

export default {
  async onLaunch() {
    if (hasRefreshToken()) {
      await renewSession().catch(() => false)
    }
  },
}
</script>

<style>
page {
  min-height: 100%;
  background: #f7f9fc;
  color: #182230;
  font-family:
    Inter, "PingFang SC", "Microsoft YaHei", -apple-system, BlinkMacSystemFont,
    sans-serif;
  font-size: 28rpx;
}

view,
text,
image,
video,
camera,
input,
button {
  box-sizing: border-box;
}

button {
  margin: 0;
}

button::after {
  border: 0;
}

.sf-page button,
.login-page button,
.sf-page uni-button,
.login-page uni-button {
  min-height: 88rpx !important;
}

button:focus-visible,
uni-button:focus-visible,
input:focus-visible,
slider:focus-visible,
picker:focus-visible {
  outline: 6rpx solid #2e2e9f;
  outline-offset: 4rpx;
}

.sf-a11y-large .sf-subheading,
.sf-a11y-large .sf-section-title,
.sf-a11y-large .sf-label,
.sf-a11y-large button,
.sf-a11y-large input,
.sf-a11y-large [class*="__desc"],
.sf-a11y-large [class*="__meta"],
.sf-a11y-large [class*="__help"],
.sf-a11y-large [class*="__value"] {
  font-size: 32rpx !important;
  line-height: 1.65 !important;
}

.sf-a11y-high-contrast {
  background: #ffffff !important;
  color: #000000 !important;
}

.sf-a11y-high-contrast .sf-surface,
.sf-a11y-high-contrast .sf-input,
.sf-a11y-high-contrast button {
  border-color: #111111 !important;
  box-shadow: none !important;
}

.sf-a11y-high-contrast text,
.sf-a11y-high-contrast .sf-muted {
  color: #111111;
}

.sf-a11y-high-contrast .sf-button--primary {
  border-color: #1f1f8f !important;
  background: #1f1f8f !important;
  color: #ffffff !important;
}

.sf-page {
  min-height: 100vh;
  padding: calc(var(--status-bar-height) + 28rpx) 28rpx 48rpx;
  background: #f7f9fc;
}

.sf-page--tab {
  padding-bottom: calc(56rpx + env(safe-area-inset-bottom));
}

.sf-topbar {
  min-height: 76rpx;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20rpx;
  margin-bottom: 28rpx;
}

.sf-brand {
  color: #5b5bd6;
  font-size: 32rpx;
  font-weight: 750;
  letter-spacing: -0.5rpx;
}

.sf-heading {
  display: block;
  color: #182230;
  font-size: 44rpx;
  line-height: 1.22;
  font-weight: 760;
  letter-spacing: -1rpx;
}

.sf-subheading {
  display: block;
  margin-top: 12rpx;
  color: #667085;
  font-size: 27rpx;
  line-height: 1.65;
}

.sf-section-title {
  display: block;
  margin-bottom: 18rpx;
  color: #182230;
  font-size: 30rpx;
  line-height: 1.4;
  font-weight: 700;
}

.sf-surface {
  background: #ffffff;
  border: 1rpx solid #e6eaf2;
  border-radius: 28rpx;
}

.sf-button {
  min-height: 88rpx;
  padding: 0 30rpx;
  border-radius: 20rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #ffffff;
  border: 1rpx solid #d0d5dd;
  color: #344054;
  font-size: 29rpx;
  line-height: 1;
  font-weight: 650;
}

.sf-button--primary {
  background: #5b5bd6;
  border-color: #5b5bd6;
  color: #ffffff;
}

.sf-button--primary:active {
  background: #4747c6;
}

.sf-button--danger {
  color: #d92d20;
  border-color: #fecdca;
  background: #fffbfa;
}

.sf-button[disabled] {
  opacity: 0.58;
}

.sf-field {
  margin-top: 26rpx;
}

.sf-label {
  display: block;
  margin-bottom: 12rpx;
  color: #344054;
  font-size: 26rpx;
  font-weight: 650;
}

.sf-input {
  width: 100%;
  min-height: 92rpx;
  padding: 0 28rpx;
  border: 1rpx solid #d0d5dd;
  border-radius: 20rpx;
  background: #ffffff;
  color: #182230;
  font-size: 29rpx;
}

.sf-input:focus {
  border-color: #5b5bd6;
}

.sf-muted {
  color: #667085;
}

.sf-status-dot {
  width: 16rpx;
  height: 16rpx;
  border-radius: 50%;
  background: #98a2b3;
}

.sf-status-dot--ready {
  background: #0e9384;
}

.sf-error {
  margin-top: 18rpx;
  padding: 20rpx 22rpx;
  border: 1rpx solid #fecdca;
  border-radius: 18rpx;
  background: #fffbfa;
  color: #b42318;
  font-size: 25rpx;
  line-height: 1.55;
}

.sf-safe-bottom {
  height: env(safe-area-inset-bottom);
}
</style>
