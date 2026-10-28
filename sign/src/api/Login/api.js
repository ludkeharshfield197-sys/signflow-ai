import requestUtil from '@/util/request';
import qs from 'qs';

// 登录 API
export function userLogin(loginData) {
    return requestUtil.post(`user/login?${qs.stringify(loginData)}`);
}
export function userRegister(registerData) {
    return requestUtil.post('user/register', registerData);
}
