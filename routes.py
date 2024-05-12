import hashlib
from flask import render_template, request, session, redirect, url_for
from db.DataBaseController import DBController

class Routes:
	def __init__(self, app):
		self.app = app
		self.dbController = DBController()
		self.create_routes()

	def create_routes(self):
		@self.app.route('/')
		def index():
			pageId = 1
			posts = self.dbController.getPostsOnPage(pageId)
			numberOfpages = self.dbController.getNumberOfPages()
			return render_template(
				'index.html',
				posts = posts,
				pageId = pageId,
				numberOfpages = numberOfpages
			)

		@self.app.route('/<int:pageId>')
		def explore(pageId):
			posts = self.dbController.getPostsOnPage(pageId)
			numberOfpages = self.dbController.getNumberOfPages()
			return render_template(
				'index.html',
				posts = posts,
				pageId = pageId,
				numberOfpages = numberOfpages
			)


		@self.app.route('/post/<int:postId>')
		def post(postId):
			post = self.dbController.getPostById(int(postId))[0]
			postComments = self.dbController.getCommentsByPostId(int(postId))
			comments = []
			for item in postComments:
				author = self.dbController.getUserById(item[3])[0][1]
				comments.append((item[0], item[1], item[2], author))

			return render_template(
				'post.html',
				post = post,
				comments = comments
			)

		@self.app.route('/profile')
		def profile():
			return render_template(
				'profile.html',
				errorText = ''
			)

		@self.app.route('/auth')
		def auth():
			return render_template(
				'auth.html',
				errorText = ''
			)
		
		@self.app.route('/createAccount')
		def createAccount():
			return render_template(
				'createAccount.html',
				errorText = ''
			)

		@self.app.route('/signup', methods=['POST'])
		def signup():
			username = request.form['username']
			password = request.form['password']
			repeatpassword = request.form['repeatpassword']

			if password != repeatpassword:
				return render_template(
					'createAccount.html',
					errorText = "Пароли не совпадают"
				)

			user = self.dbController.getUserByUsername(username)
			if user:
				return render_template(
					'createAccount.html',
					errorText = 'Пользователь уже существует'
				)
			else:
				self.dbController.addUser(username, password, "user")
				return redirect(url_for('index'))

		@self.app.route('/login', methods=['POST'])
		def login():
			username = request.form['username']
			password = request.form['password']

			user = self.dbController.getUserByUsername(username)

			if user:
				hashOfpassword = hashlib.sha256(password.encode()).hexdigest()

				if user[0][2] == hashOfpassword:
					session['username'] = username
					session['role'] = user[0][3]
				else:
					return render_template(
						'auth.html',
						errorText = "Неверный пароль",
					)
			else:
				return render_template(
						"auth.html",
						errorText = "Неверный логин"
					)

			return redirect(url_for('index'))

		@self.app.route('/changePassword', methods=['POST'])
		def changePassword():
			username = session['username']
			password = request.form['password']
			newPassword = request.form['newpassword']

			user = self.dbController.getUserByUsername(username)

			if user:
				hashOfpassword = hashlib.sha256(password.encode()).hexdigest()

				if user[0][2] == hashOfpassword:
					hashOfnewPassword = hashlib.sha256(newPassword.encode()).hexdigest()
					self.dbController.setUserPasswordByUsername(user[0][1], hashOfnewPassword)
				else:
					return render_template(
						'profile.html',
						errorText = "Неверный текущий пароль",
					)

			return render_template(
				'profile.html',
				errorText = "Пароль успешно обновлен"
			)

		@self.app.route('/logout')
		def logout():
			session.pop('username', None)
			session.pop('role', None)
			return redirect(url_for('index'))

		@self.app.route('/newPost')
		def newPost():
			return render_template(
				'newPost.html'
			)

		@self.app.route('/sendNewPost', methods=['POST'])
		def sendNewPost():
			if session['role'] != 'admin':
				return "Доступ запрещен!"
			title = request.form['title']
			content = request.form['content']

			if 'username' in session:
				self.dbController.addPost(title, content)
				return redirect(url_for('index'))
			else:
				return redirect(url_for('index'))
		
		@self.app.route('/sendNewComment/<int:postId>', methods=['POST'])
		def sendNewComment(postId):
			content = request.form['content']
	
			if 'username' in session:
				userId = self.dbController.getUserByUsername(session['username'])[0][0]				
				self.dbController.addComment(postId, content, userId)
				return redirect(url_for('index'))
			else:
				return redirect(url_for('index'))
		
		@self.app.route('/deletePost/<int:post_id>')
		def deletePost(post_id):
			if 'role' in session:
				if session['role'] != 'admin':
					return "Доступ запрещен!"
			else:
				return "Доступ запрещен!"

			self.dbController.deletePostByID(post_id)
			return redirect(url_for('index'))

		@self.app.route('/editPost/<int:post_id>')
		def editPost(post_id):
			if 'role' in session:
				if session['role'] != 'admin':
					return "Доступ запрещен!"
			else:
				return "Доступ запрещен!"

			return render_template(
				'editPost.html',
				post = self.dbController.getPostById(int(post_id))[0]
			)

		@self.app.route('/sendEditPost/<int:post_id>', methods=['POST'])
		def sendEditPost(post_id):
			if 'role' in session:
				if session['role'] != 'admin':
					return "Доступ запрещен!"
			else:
				return "Доступ запрещен!"

			title = request.form['title']
			content = request.form['content']

			if 'username' in session:
				self.dbController.updatePostByID(post_id, title, content)
				return redirect(url_for('index'))
			else:
				return redirect(url_for('index'))