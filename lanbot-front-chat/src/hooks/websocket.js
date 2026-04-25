import  WS_ADDRESS  from "@/configs";

function useWebSocket(handleMessage){
    const ws = new WebSocket(WS_ADDRESS);

    const init = () => {
        bindEvent();
    }

    function bindEvent(){
        ws.addEventListener('open', handleOpen, false);
        ws.addEventListener('close', handleClose, false);
        ws.addEventListener('error', handleError, false);
        ws.addEventListener('message', handleMessage, false);
    }

    function handleOpen (e) {
        console.log('Wensocket open', e);
    }

    function handleClose (e) {
        console.log('Wensocket close', e);
    }

    function handleError (e) {
        console.log('Wensocket error', e);
    }

    init();
    return ws;
}

export {useWebSocket};