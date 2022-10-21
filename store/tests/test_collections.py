from store.models import Collection
from rest_framework import status
import pytest
from model_bakery import baker

@pytest.fixture
def create_collection(api_client):
    def do_create_collection(collection):
        return api_client.post('/store/collections/', collection)
    return do_create_collection

@pytest.fixture
def update_collection(api_client):
    def do_update_collection(title):
        collection = baker.make(Collection)
        return api_client.put(f'/store/collections/{collection.id}/', {'title': title})
    return do_update_collection

@pytest.fixture
def delete_collection(api_client):
    def do_delete_collection():
        collection = baker.make(Collection)
        return api_client.delete(f'/store/collections/{collection.id}/')
    return do_delete_collection

@pytest.mark.django_db
class TestCreateCollection:
    def test_if_user_is_anonymous_returns_401(self, create_collection):
        # Arrange

        # Act
        response = create_collection({'title': 'a'})

        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_if_user_is_not_admin_returns_403(self, api_client, create_collection, authenticate):
        authenticate(is_staff=False)

        response = create_collection({'title': 'a'})

        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_if_data_is_invalid_returns_400(self, api_client, create_collection, authenticate):
        authenticate(is_staff=True)

        response = create_collection({'title': ''})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['title'] is not None
    
    def test_if_data_is_valid_returns_201(self, api_client, create_collection, authenticate):
        authenticate(is_staff=True)

        response = create_collection({'title': 'a'})

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['id'] > 0

@pytest.mark.django_db
class TestRetrieveCollection:
    def test_if_collection_exists_returns_200(self, api_client):
        collection = baker.make(Collection)

        response = api_client.get(f'/store/collections/{collection.id}/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data == {
            'id': collection.id,
            'title': collection.title,
            'products_count': 0
        }
    
    def test_if_user_is_admin_returns_200(self, api_client, authenticate):
        authenticate(is_staff=True)
        collection = baker.make(Collection)

        response = api_client.get(f'/store/collections/{collection.id}/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data == {
            'id': collection.id,
            'title': collection.title,
            'products_count': 0
        }

@pytest.mark.django_db
class TestUpdateCollection:
    def test_if_user_is_anonymous_returns_401(self, update_collection):
        response = update_collection('aa')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_if_user_is_not_admin_returns_403(self, update_collection, authenticate):
        authenticate(is_staff=False)

        response = update_collection('aa')

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_data_is_invalid_returns_400(self, update_collection, authenticate):
        authenticate(is_staff=True)

        response = update_collection('')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_if_data_is_valid_returns_201(self, update_collection, authenticate):
        authenticate(is_staff=True)

        response = update_collection('aa')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == 'aa'

@pytest.mark.django_db
class TestDeleteCollection:
    def test_if_user_is_anonymous_returns_401(self, delete_collection):
        response = delete_collection()

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_if_user_is_not_admin_returns_403(self, delete_collection, authenticate):
        authenticate(is_staff=False)

        response = delete_collection()

        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_if_user_is_admin_returns_204(self, delete_collection, authenticate):
        authenticate(is_staff=True)

        response = delete_collection()

        assert response.status_code == status.HTTP_204_NO_CONTENT
