// Toast function
function showSuccessToast({message = ""}) {
    toast({
        title: "Thành công!",
        message: message != "" ? message : 'Tạo thành công',
        type: "success",
        duration: 5000
    });
}

function showErrorToast({message = ""}) {
    toast({
        title: "Thất bại!",
        message: message != "" ? message : "Vui lòng xem lại link!.",
        type: "error",
        duration: 5000
    });
}

function toast({
                   title = "",
                   message = "",
                   type = "info",
                   duration = 3000
               }) {
    const main = document.getElementById("toast");
    if (main) {
        const toast = document.createElement("div");

        //Auto remove toast
        const autoRemoveId = setTimeout(function () {
            main.removeChild(toast);
        }, duration + 1000);

        // Remove toast when clicked
        toast.onclick = function (e) {
            if (e.target.closest(".toast__close")) {
                main.removeChild(toast);
                clearTimeout(autoRemoveId);
            }
        };

        // cac loai icon
        const icons = {
            success: "fas fa-check-circle",
            info: "fas fa-info-circle",
            warning: "fas fa-exclamation-circle",
            error: "fas fa-exclamation-circle"
        };
        //
        // // khai bao type
        const icon = icons[type];
        const delay = (duration / 1000).toFixed(2);
        //
        // //add class
        // toast.classList.add("toast")
        toast.classList.add("toast", `toast--${type}`);

        toast.style.animation = `slideInLeft_1 ease .3s, fadeOut_1 linear 1s ${delay}s forwards`;
        toast.style.animation = `slideInLeft_1 ease 1s`;

        toast.innerHTML = `
                    <div class="toast__icon">
                        <i class="${icon}"></i>
                    </div>
                    <div class="toast__body">
                        <h3 class="toast__title">${title}</h3>
                        <p class="toast__msg">${message}</p>
                    </div>
                    <div class="toast__close">
                        <i class="fas fa-times"></i>
                    </div>
                `;


        main.appendChild(toast);
    }
}
