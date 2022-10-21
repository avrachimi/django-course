from store.models import Collection, Product
from rest_framework import status
import pytest
from model_bakery import baker

@pytest.fixture
def create_product(api_client):
    def do_create_product(product):
        return api_client.post('/store/products/', product)
    return do_create_product

@pytest.fixture
def update_product_put(api_client):
    def do_update_product_put(updated_product):
        product = baker.make(Product)
        updated_product['id'] = product.id
        updated_product['collection'] = product.collection.id
        return api_client.put(f'/store/products/{product.id}/', updated_product)
    return do_update_product_put

@pytest.fixture
def update_product_patch(api_client):
    def do_update_product_patch(product_fields):
        product = baker.make(Product)
        product_fields['id'] = product.id
        return api_client.patch(f'/store/products/{product.id}/', product_fields)
    return do_update_product_patch

@pytest.fixture
def delete_product(api_client):
    def do_delete_product():
        product = baker.make(Product)
        return api_client.delete(f'/store/products/{product.id}/')
    return do_delete_product

@pytest.mark.django_db
class TestCreateProduct:
    def test_if_user_is_anonymous_returns_401(self, create_product):
        # Arrange

        # Act
        response = create_product({})

        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_if_user_is_not_admin_returns_403(self, api_client, create_product, authenticate):
        authenticate(is_staff=False)

        response = create_product({})

        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_if_data_is_invalid_returns_400(self, create_product, authenticate):
        authenticate(is_staff=True)
        

        response = create_product({'title': 'a'})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_if_data_is_valid_returns_201(self, create_product, authenticate):
        authenticate(is_staff=True)
        collection = baker.make(Collection)
        product = {
            'title': 'a',
            'description': 'aa',
            'slug': '-',
            'inventory': 10,
            'unit_price': 5.5,
            'collection': collection.id
        }

        response = create_product(product)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['title'] == 'a'
        assert response.data['unit_price'] == 5.5

@pytest.mark.django_db
class TestRetrieveProduct:
    def test_if_product_exists_returns_200(self, api_client):
        product = baker.make(Product)

        response = api_client.get(f'/store/products/{product.id}/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == product.id
    
    def test_if_user_is_admin_returns_200(self, api_client, authenticate):
        authenticate(is_staff=True)
        product = baker.make(Product)

        response = api_client.get(f'/store/products/{product.id}/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == product.id

@pytest.mark.django_db
class TestUpdateProduct:
    def test_if_user_is_anonymous_returns_401(self, update_product_put):
        response = update_product_put({'title':'aa'})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_if_user_is_not_admin_returns_403(self, update_product_put, authenticate):
        authenticate(is_staff=False)

        response = update_product_put({'title': 'aa'})

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_data_is_invalid_put_returns_400(self, update_product_put, authenticate):
        authenticate(is_staff=True)
        product = {
            'id': 0,
            'title': 'aaaa',
            'description': 'aa',
            'slug': '-',
            'inventory': 10,
            'unit_price': -5.0, # Invalid data
            'collection': 1
        }

        response = update_product_put(product)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_if_data_is_valid_put_returns_201(self, update_product_put, authenticate):
        authenticate(is_staff=True)
        product = {
            'id': 0,
            'title': 'aaaa',
            'description': 'aa',
            'slug': '-',
            'inventory': 10,
            'unit_price': 5.0,
            'collection': 1
        }

        response = update_product_put(product)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == 'aaaa'
    
    def test_if_data_is_invalid_patch_returns_400(self, update_product_patch, authenticate):
        authenticate(is_staff=True)
        product = {
            'id': 0,
            'unit_price': -5.0
        }

        response = update_product_patch(product)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_if_data_is_valid_patch_returns_201(self, update_product_patch, authenticate):
        authenticate(is_staff=True)
        product = {
            'id': 0,
            'unit_price': 5.0
        }

        response = update_product_patch(product)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['unit_price'] == 5.0

@pytest.mark.django_db
class TestDeleteProduct:
    def test_if_user_is_anonymous_returns_401(self, delete_product):
        response = delete_product()

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_if_user_is_not_admin_returns_403(self, delete_product, authenticate):
        authenticate(is_staff=False)

        response = delete_product()

        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_if_user_is_admin_returns_204(self, delete_product, authenticate):
        authenticate(is_staff=True)

        response = delete_product()

        assert response.status_code == status.HTTP_204_NO_CONTENT
