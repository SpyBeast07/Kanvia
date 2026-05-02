interface DialogState {
    show: boolean;
    title: string;
    message: string;
    type: 'alert' | 'confirm' | 'prompt';
    inputValue?: string;
    onConfirm?: (value?: string) => void;
    onCancel?: () => void;
}

class UIStore {
    dialog = $state<DialogState>({
        show: false,
        title: '',
        message: '',
        type: 'alert'
    });

    activeFilter = $state<'assigned' | 'added' | null>(null);
    taskSearchQuery = $state('');

    alert(message: string, title = 'Notification') {
        this.dialog = { 
            show: true, 
            title, 
            message, 
            type: 'alert',
            onConfirm: () => this.close()
        };
    }

    confirm(message: string, title = 'Confirm Action'): Promise<boolean> {
        return new Promise((resolve) => {
            this.dialog = {
                show: true,
                title,
                message,
                type: 'confirm',
                onConfirm: () => {
                    this.close();
                    resolve(true);
                },
                onCancel: () => {
                    this.close();
                    resolve(false);
                }
            };
        });
    }

    prompt(message: string, title = 'Input Required', defaultValue = ''): Promise<string | null> {
        return new Promise((resolve) => {
            this.dialog = {
                show: true,
                title,
                message,
                type: 'prompt',
                inputValue: defaultValue,
                onConfirm: (val) => {
                    this.close();
                    resolve(val || '');
                },
                onCancel: () => {
                    this.close();
                    resolve(null);
                }
            };
        });
    }

    close() {
        this.dialog.show = false;
    }
}

export const ui = new UIStore();
