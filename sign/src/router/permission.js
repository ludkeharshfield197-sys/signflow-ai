import router from "@/router/index"

router.beforeEach((to,from,next)=>{
    const whiteList=['/login','/register','/home'] // 白名单
    let token = window.localStorage.getItem("token")
    if(token){
        next();
    }else{
        if(whiteList.includes(to.path)){
            next();
        }else{
            next("/login");
        }
    }
})
