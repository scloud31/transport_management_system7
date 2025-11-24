class PostsManager {
    constructor() {
        this.postsList = document.getElementById('postsList');
        this.init();
    }

    init() {
        this.loadPosts();
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Обработчик для модального окна добавления поста
        document.getElementById('addPostForm')?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.addPost();
        });
    }

    loadPosts() {
        fetch('/api/posts')
            .then(response => response.json())
            .then(posts => {
                this.renderPosts(posts);
            })
            .catch(error => {
                console.error('Ошибка загрузки постов:', error);
            });
    }

    renderPosts(posts) {
        if (!this.postsList) return;

        this.postsList.innerHTML = '';

        if (posts.length === 0) {
            this.postsList.innerHTML = `
                <div class="list-group-item text-center text-muted">
                    Посты не добавлены
                </div>
            `;
            return;
        }

        posts.forEach(post => {
            const postElement = this.createPostElement(post);
            this.postsList.appendChild(postElement);
        });
    }

    createPostElement(post) {
        const div = document.createElement('div');
        div.className = 'list-group-item d-flex justify-content-between align-items-center';
        div.innerHTML = `
            <div>
                <strong>${this.escapeHtml(post.name)}</strong>
                ${post.description ? `<br><small class="text-muted">${this.escapeHtml(post.description)}</small>` : ''}
            </div>
            <div>
                <button class="btn btn-sm btn-danger" onclick="postsManager.deletePost(${post.id})">
                    <i class="bi bi-trash"></i>
                </button>
            </div>
        `;
        return div;
    }

    showAddModal() {
        // Очищаем форму
        document.getElementById('postName').value = '';
        document.getElementById('postDescription').value = '';
        
        // Показываем модальное окно
        const modal = new bootstrap.Modal(document.getElementById('addPostModal'));
        modal.show();
    }

    addPost() {
        const name = document.getElementById('postName').value.trim();
        const description = document.getElementById('postDescription').value.trim();

        if (!name) {
            this.showAlert('Введите название поста', 'warning');
            return;
        }

        fetch('/api/posts', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                name: name,
                description: description
            })
        })
        .then(response => response.json())
        .then(newPost => {
            // Закрываем модальное окно
            const modal = bootstrap.Modal.getInstance(document.getElementById('addPostModal'));
            modal.hide();

            // Перезагружаем список постов
            this.loadPosts();
            
            this.showAlert('Пост успешно добавлен', 'success');
        })
        .catch(error => {
            console.error('Ошибка:', error);
            this.showAlert('Ошибка при добавлении поста', 'danger');
        });
    }

    deletePost(postId) {
        if (!confirm('Вы уверены, что хотите удалить этот пост?')) {
            return;
        }

        fetch(`/api/posts/${postId}`, {
            method: 'DELETE'
        })
        .then(response => response.json())
        .then(result => {
            if (result.success) {
                this.loadPosts();
                this.showAlert('Пост успешно удален', 'success');
            } else {
                this.showAlert(result.error || 'Ошибка при удалении поста', 'danger');
            }
        })
        .catch(error => {
            console.error('Ошибка:', error);
            this.showAlert('Ошибка при удалении поста', 'danger');
        });
    }

    showAlert(message, type) {
        // Создаем уведомление
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        alertDiv.style.cssText = `
            top: 20px;
            right: 20px;
            z-index: 9999;
            min-width: 300px;
        `;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        document.body.appendChild(alertDiv);

        // Автоматически скрываем через 5 секунд
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Инициализация менеджера постов
let postsManager;

document.addEventListener('DOMContentLoaded', function() {
    postsManager = new PostsManager();
});