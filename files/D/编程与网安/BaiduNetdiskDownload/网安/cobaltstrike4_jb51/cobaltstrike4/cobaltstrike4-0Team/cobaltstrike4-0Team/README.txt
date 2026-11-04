================cobalt strike 4.0 自签名版================


能对上hash的原版，自行复制2个文件jar包就能用了,
对cobaltstrike的源码只做过一行改动
对哈希: certutil -hashfile cobaltstrike.jar sha256
官网hash:558f61bfab60ef5e6bec15c8a6434e94249621f53e7838868cdb3206168a0937	

将 AuthCrypto.class 复制到 common/AuthCrypto.class
将 authkey.pub 复制到 resources/authkey.pub
将 cobaltstrike2.auth 放在和 cobaltstrike.jar 同级目录

