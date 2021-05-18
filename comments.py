class Comments:
    def like_comment(self, comment_id:int, db, Comment):
        comment = Comment.query.filter_by(id=comment_id).first()
        comment.likes += 1
        db.session.commit()


