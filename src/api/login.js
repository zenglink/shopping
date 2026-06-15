import request from '@/utils/request'
// 获取图型验证码
export const getPicCode = () => {
  return request.get('/captcha/image')
}
// 获取短信验证码
export const getMsgCode = (captchaCode, captchaKey, mobile) => {
  return request.post('/captcha/sendSmsCaptcha', {
    from: {
      captchaCode,
      captchaKey,
      mobile
    }
  })
}
// 手机验证码登录
export const codeLogin = (mobile, smsCode) => {
  return request.post(
    '/passport/login',
    {
      form: {
        isParty: false,
        partyData: {},
        mobile,
        smsCode
      }
    },
    {
      headers: {
        platform: 'H5'
      }
    }
  )
}
