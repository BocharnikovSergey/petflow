import factory

from users.models import ProjectUser, UserRole, Role


class UserFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = ProjectUser

    class Params:
        role_name = 'user'

    email = factory.LazyAttributeSequence(
        lambda obj, n:
        f'{obj.role_name}{n}@{obj.role_name}.ru'
    )
    first_name = 'Test'
    last_name = 'User'
    password = factory.PostGenerationMethodCall('set_password', 'qweQWE123!')


    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        role_name = cls._original_params.get('role_name')
        instance = super()._create(model_class, *args, **kwargs)
        instance._role_name = role_name 
        return instance

    @factory.post_generation
    def role(self, create, extracted, **kwargs):
        if create:
            role, _ = Role.objects.get_or_create(
                name=self._role_name
            )
            UserRole.objects.create(user=self, role=role)
