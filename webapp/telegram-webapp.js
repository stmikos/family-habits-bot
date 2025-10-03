/**
 * Telegram WebApp Integration для Family Habits
 * Библиотека для работы с Telegram WebApp API
 */

class TelegramWebApp {
    constructor() {
        this.isReady = false;
        this.initData = null;
        this.user = null;
        this.colorScheme = 'light';
        
        this.init();
    }

    /**
     * Инициализация Telegram WebApp
     */
    init() {
        // Проверяем, запущено ли в Telegram
        if (window.Telegram && window.Telegram.WebApp) {
            this.tg = window.Telegram.WebApp;
            this.initData = this.tg.initData;
            this.user = this.tg.initDataUnsafe?.user;
            this.colorScheme = this.tg.colorScheme;
            
            // Настраиваем WebApp
            this.tg.ready();
            this.tg.expand();
            
            // Применяем тему Telegram
            this.applyTelegramTheme();
            
            // Показываем главную кнопку если нужно
            this.setupMainButton();
            
            // Показываем кнопку назад если нужно
            this.setupBackButton();
            
            this.isReady = true;
            
            console.log('🚀 Telegram WebApp initialized:', {
                user: this.user,
                colorScheme: this.colorScheme,
                platform: this.tg.platform
            });
        } else {
            // Демо-режим для тестирования вне Telegram
            console.log('🔧 Demo mode: Running outside Telegram');
            this.setupDemoMode();
        }
    }

    /**
     * Применение темы Telegram к приложению
     */
    applyTelegramTheme() {
        const root = document.documentElement;
        
        if (this.colorScheme === 'dark') {
            root.style.setProperty('--tg-bg-color', this.tg.backgroundColor || '#212121');
            root.style.setProperty('--tg-text-color', this.tg.textColor || '#ffffff');
            root.style.setProperty('--tg-hint-color', this.tg.hintColor || '#aaaaaa');
            root.style.setProperty('--tg-button-color', this.tg.buttonColor || '#2ea6ff');
            root.style.setProperty('--tg-button-text-color', this.tg.buttonTextColor || '#ffffff');
        } else {
            root.style.setProperty('--tg-bg-color', this.tg.backgroundColor || '#ffffff');
            root.style.setProperty('--tg-text-color', this.tg.textColor || '#000000');
            root.style.setProperty('--tg-hint-color', this.tg.hintColor || '#707579');
            root.style.setProperty('--tg-button-color', this.tg.buttonColor || '#2ea6ff');
            root.style.setProperty('--tg-button-text-color', this.tg.buttonTextColor || '#ffffff');
        }

        // Добавляем класс темы к body
        document.body.classList.add(`tg-theme-${this.colorScheme}`);
    }

    /**
     * Настройка главной кнопки
     */
    setupMainButton() {
        // Настройка зависит от страницы
        const page = this.getCurrentPage();
        
        switch (page) {
            case 'registration':
                this.showMainButton('🌱 Создать семью', () => this.submitRegistration());
                break;
            case 'registration-children':
                this.showMainButton('👶 Добавить детей', () => this.submitChildren());
                break;
            case 'create-task':
                this.showMainButton('✅ Создать задачу', () => this.submitTask());
                break;
            case 'shop':
                // Главная кнопка скрыта в магазине
                this.hideMainButton();
                break;
            default:
                this.hideMainButton();
        }
    }

    /**
     * Настройка кнопки назад
     */
    setupBackButton() {
        const page = this.getCurrentPage();
        
        if (page !== 'index' && page !== 'registration') {
            this.showBackButton(() => {
                this.goBack();
            });
        }
    }

    /**
     * Показать главную кнопку
     */
    showMainButton(text, callback) {
        if (this.tg && this.tg.MainButton) {
            this.tg.MainButton.text = text;
            this.tg.MainButton.show();
            this.tg.MainButton.onClick(callback);
        }
    }

    /**
     * Скрыть главную кнопку
     */
    hideMainButton() {
        if (this.tg && this.tg.MainButton) {
            this.tg.MainButton.hide();
        }
    }

    /**
     * Показать кнопку назад
     */
    showBackButton(callback) {
        if (this.tg && this.tg.BackButton) {
            this.tg.BackButton.show();
            this.tg.BackButton.onClick(callback);
        }
    }

    /**
     * Скрыть кнопку назад
     */
    hideBackButton() {
        if (this.tg && this.tg.BackButton) {
            this.tg.BackButton.hide();
        }
    }

    /**
     * Определить текущую страницу
     */
    getCurrentPage() {
        const path = window.location.pathname;
        if (path.includes('registration-children')) return 'registration-children';
        if (path.includes('registration')) return 'registration';
        if (path.includes('create-task')) return 'create-task';
        if (path.includes('shop')) return 'shop';
        if (path.includes('profile')) return 'profile';
        if (path.includes('statistics')) return 'statistics';
        if (path.includes('welcome')) return 'welcome';
        return 'index';
    }

    /**
     * Переход назад
     */
    goBack() {
        const page = this.getCurrentPage();
        
        switch (page) {
            case 'registration-children':
                window.location.href = 'registration.html';
                break;
            case 'welcome':
                window.location.href = 'index.html';
                break;
            case 'profile':
            case 'shop':
            case 'statistics':
            case 'create-task':
                window.location.href = 'index.html';
                break;
            default:
                window.history.back();
        }
    }

    /**
     * Отправка данных регистрации
     */
    async submitRegistration() {
        const form = document.getElementById('registrationForm');
        if (!form) return;

        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());
        
        // Добавляем данные пользователя Telegram
        data.telegram_user = this.user;
        data.telegram_init_data = this.initData;

        try {
            this.showProgress('Создание семейного профиля...');
            
            // Отправляем данные на сервер
            await this.sendToBot('/api/registration', data);
            
            // Переходим к добавлению детей
            window.location.href = 'registration-children.html';
        } catch (error) {
            this.showAlert('Ошибка создания семьи: ' + error.message);
        }
    }

    /**
     * Отправка данных о детях
     */
    async submitChildren() {
        const children = this.getChildrenData();
        
        try {
            this.showProgress('Добавление детей в семью...');
            
            await this.sendToBot('/api/children', { 
                children,
                telegram_user: this.user 
            });
            
            window.location.href = 'welcome.html';
        } catch (error) {
            this.showAlert('Ошибка добавления детей: ' + error.message);
        }
    }

    /**
     * Отправка задачи
     */
    async submitTask() {
        const form = document.getElementById('taskForm');
        if (!form) return;

        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());
        
        data.telegram_user = this.user;

        try {
            this.showProgress('Создание задачи...');
            
            await this.sendToBot('/api/tasks/create', data);
            
            this.showAlert('✅ Задача успешно создана!');
            setTimeout(() => {
                window.location.href = 'index.html';
            }, 1500);
        } catch (error) {
            this.showAlert('Ошибка создания задачи: ' + error.message);
        }
    }

    /**
     * Получение данных о детях из формы
     */
    getChildrenData() {
        const children = [];
        const childCards = document.querySelectorAll('.child-card');
        
        childCards.forEach((card, index) => {
            const nameInput = card.querySelector(`input[name="child_name_${index}"]`);
            const ageInput = card.querySelector(`input[name="child_age_${index}"]`);
            const avatarInput = card.querySelector(`input[name="child_avatar_${index}"]:checked`);
            
            if (nameInput && nameInput.value.trim()) {
                children.push({
                    name: nameInput.value.trim(),
                    age: parseInt(ageInput?.value) || 6,
                    avatar: avatarInput?.value || '👶'
                });
            }
        });
        
        return children;
    }

    /**
     * Отправка данных в бот
     */
    async sendToBot(endpoint, data) {
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }

        return await response.json();
    }

    /**
     * Показать прогресс
     */
    showProgress(message) {
        if (this.tg && this.tg.MainButton) {
            this.tg.MainButton.showProgress();
            this.tg.MainButton.text = message;
        }
    }

    /**
     * Скрыть прогресс
     */
    hideProgress() {
        if (this.tg && this.tg.MainButton) {
            this.tg.MainButton.hideProgress();
        }
    }

    /**
     * Показать алерт
     */
    showAlert(message) {
        if (this.tg && this.tg.showAlert) {
            this.tg.showAlert(message);
        } else {
            alert(message);
        }
    }

    /**
     * Показать подтверждение
     */
    showConfirm(message, callback) {
        if (this.tg && this.tg.showConfirm) {
            this.tg.showConfirm(message, callback);
        } else {
            if (confirm(message)) {
                callback(true);
            } else {
                callback(false);
            }
        }
    }

    /**
     * Настройка демо-режима
     */
    setupDemoMode() {
        this.user = {
            id: 123456789,
            first_name: 'Demo',
            last_name: 'User',
            username: 'demo_user'
        };
        this.isReady = true;
        
        // Эмулируем кнопки Telegram
        this.createDemoButtons();
    }

    /**
     * Создание демо-кнопок для тестирования
     */
    createDemoButtons() {
        const demoPanel = document.createElement('div');
        demoPanel.id = 'demo-panel';
        demoPanel.style.cssText = `
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: #2ea6ff;
            color: white;
            padding: 10px;
            display: flex;
            gap: 10px;
            justify-content: center;
            z-index: 10000;
        `;
        
        const mainBtn = document.createElement('button');
        mainBtn.textContent = 'Main Button';
        mainBtn.style.cssText = 'padding: 8px 16px; border: none; border-radius: 4px; background: white; color: #2ea6ff; cursor: pointer;';
        mainBtn.onclick = () => this.demoMainButtonClick();
        
        const backBtn = document.createElement('button');
        backBtn.textContent = '← Back';
        backBtn.style.cssText = 'padding: 8px 16px; border: none; border-radius: 4px; background: rgba(255,255,255,0.2); color: white; cursor: pointer;';
        backBtn.onclick = () => this.goBack();
        
        demoPanel.appendChild(backBtn);
        demoPanel.appendChild(mainBtn);
        document.body.appendChild(demoPanel);
        
        this.demoMainButton = mainBtn;
        this.demoBackButton = backBtn;
        
        // Настраиваем кнопки для текущей страницы
        this.setupMainButton();
        this.setupBackButton();
    }

    /**
     * Обработчик клика по демо главной кнопке
     */
    demoMainButtonClick() {
        const page = this.getCurrentPage();
        
        switch (page) {
            case 'registration':
                this.submitRegistration();
                break;
            case 'registration-children':
                this.submitChildren();
                break;
            case 'create-task':
                this.submitTask();
                break;
        }
    }

    /**
     * Получить параметры URL
     */
    getUrlParams() {
        const params = new URLSearchParams(window.location.search);
        return {
            user_id: params.get('user_id'),
            family_id: params.get('family_id'),
            first_name: params.get('first_name'),
            stars: params.get('stars'),
            tab: params.get('tab')
        };
    }

    /**
     * Закрыть WebApp
     */
    close() {
        if (this.tg && this.tg.close) {
            this.tg.close();
        } else {
            window.close();
        }
    }
}

// Глобальная инициализация
window.telegramApp = new TelegramWebApp();

// Экспорт для использования в других скриптах
window.TelegramWebApp = TelegramWebApp;