from rest_framework import permissions


class IsQuizzer(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_quizzer


class IsQuizzeeReader(permissions.BasePermission):
    def has_permission(self, request, view):
        return not request.user.is_quizzer and view.action in ["list", "retrieve"]


class IsQuizzeeSubmiter(permissions.BasePermission):
    def has_permission(self, request, view):
        return not request.user.is_quizzer and view.action == "submit"


class IsQuizzerNotSubmiter(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_quizzer and view.action != "submit"


class IsQuizzee(permissions.BasePermission):
    def has_permission(self, request, view):
        return not request.user.is_quizzer


class IsQuizzerReader(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_quizzer and view.action in ["list", "retrieve"]
