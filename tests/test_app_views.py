from datetime import date
from http import HTTPStatus
from typing import Callable

import pytest
from aiohttp.test_utils import TestClient

from invest_api import Company
from invest_api.utils import is_valid_uuid


class TestPingView:
    url = "/ping"

    async def test_that_route_is_named(self, client: TestClient) -> None:
        url = client.app.router["ping"].url_for()

        assert self.url == str(url)

    async def test_that_service_is_alive(self, client: TestClient) -> None:
        response = await client.get(self.url)
        assert response.status == HTTPStatus.OK

        assert await response.json() == {
            "data": None,
            "message": "pong",
        }

        request_id = response.headers.get("X-Request-ID")
        assert is_valid_uuid(request_id)


class TestHealthView:
    url = "/health"

    async def test_that_route_is_named(self, client: TestClient) -> None:
        url = client.app.router["health"].url_for()

        assert self.url == str(url)

    async def test_that_service_is_alive(self, client: TestClient) -> None:
        response = await client.get(self.url)
        assert response.status == HTTPStatus.OK

        assert await response.json() == {
            "data": None,
            "message": "OK",
        }

        request_id = response.headers.get("X-Request-ID")
        assert is_valid_uuid(request_id)


class TestCompanyDetailsView:
    url = "/companies/{id}"

    @pytest.mark.parametrize("identifier", [
        "8887776655",
        "88877766554433",
    ])
    async def test_request_with_not_existing_company(
            self,
            client: TestClient,
            identifier: str,
    ) -> None:
        url = self.url.format(id=identifier)

        response = await client.get(url)
        assert response.status == HTTPStatus.NOT_FOUND

        assert await response.json() == {
            "message": "Not found",
        }

    @pytest.mark.parametrize("identifier_key", [
        "itn",
        "psrn",
    ])
    async def test_request_with_existing_company(
            self,
            client: TestClient,
            create_company: Callable,
            identifier_key: str,
    ) -> None:
        company = Company(
            id=1,
            name="ЗАО ОКБ",
            size="Крупная",
            registered_at=date(2010, 1, 1),
            itn="7710561081",
            psrn="1047796788819",
            region_code="77",
            region_name="Москва",
            activity_code="5",
            activity_name="Высокая",
            charter_capital=1200,
            is_acting=True,
            is_liquidating=False,
            not_reported_last_year=True,
            not_in_same_registry=False,
            ceo_has_other_companies=True,
            negative_list_risk=False,
            bankruptcy_probability=5,
            bankruptcy_vars=None,
            is_enough_finance_data=True,
            relative_success=7,
            revenue_forecast=25000,
            assets_forecast=20000,
            dev_stage="Развивается активно",
            dev_stage_coordinates=None,
        )
        create_company(company)

        identifier = getattr(company, identifier_key)
        url = self.url.format(id=identifier)

        response = await client.get(url)
        assert response.status == HTTPStatus.OK

        data = company.to_dict()

        assert await response.json() == {
            "data": data,
            "message": "OK",
        }


class TestCompaniesQueryView:
    url = "/companies/query"

    async def test_request_without_query_params(
            self,
            client: TestClient,
    ) -> None:
        response = await client.get(self.url)
        assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY

        assert await response.json() == {
            "errors": {
                "name": ["Missing data for required field."],
            },
            "message": "Input payload validation failed",
        }

    async def test_request_with_undefined_company_name(
            self,
            client: TestClient,
    ) -> None:
        params = {
            "name": "undefined",
        }

        response = await client.get(self.url, params=params)
        assert response.status == HTTPStatus.OK

        assert await response.json() == {
            "data": [],
            "message": "OK",
        }

    async def test_request_with_existing_company(
            self,
            client: TestClient,
            create_company: Callable,
    ) -> None:
        company = Company(
            id=1,
            name="ОАО Ёжики и Грибочки",
            size="Микропредприятие",
            registered_at=date(2010, 1, 1),
            itn="2464222938",
            psrn="1102454000670",
            region_code="77",
            region_name="Москва",
            activity_code="47.51.1",
            activity_name="Семейный подряд",
            charter_capital=1000,
            is_acting=True,
            is_liquidating=False,
            not_reported_last_year=True,
            not_in_same_registry=False,
            ceo_has_other_companies=True,
            negative_list_risk=False,
            bankruptcy_probability=5,
            bankruptcy_vars=None,
            is_enough_finance_data=True,
            relative_success=7,
            revenue_forecast=25000,
            assets_forecast=20000,
            dev_stage="Рост активов",
            dev_stage_coordinates=None,
        )
        create_company(company)

        params = {
            "name": "ежеки",
        }

        response = await client.get(self.url, params=params)
        assert response.status == HTTPStatus.OK

        assert await response.json() == {
            "data": [
                company.to_dict(),
            ],
            "message": "OK",
        }


class TestCompaniesSelectionView:
    url = "/companies/selection"

    async def test_request_without_query_params(
            self,
            client: TestClient,
    ) -> None:
        response = await client.get(self.url)
        assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY

        missing_required_field = ["Missing data for required field."]

        assert await response.json() == {
            "errors": {
                "size": missing_required_field,
                "region_codes": missing_required_field,
                "is_acting": missing_required_field,
                "is_liquidating": missing_required_field,
                "not_reported_last_year": missing_required_field,
                "not_in_same_registry": missing_required_field,
                "ceo_has_other_companies": missing_required_field,
                "negative_list_risk": missing_required_field,
                "bankruptcy_probability": missing_required_field,
            },
            "message": "Input payload validation failed",
        }

    async def test_request_with_existing_company(
            self,
            client: TestClient,
            create_company: Callable,
    ) -> None:
        company = Company(
            id=1,
            name="ЗАО ОКБ",
            size="Крупная",
            registered_at=date(2010, 1, 1),
            itn="7710561081",
            psrn="1047796788819",
            region_code="77",
            region_name="Москва",
            activity_code="5",
            activity_name="Высокая",
            charter_capital=1200,
            is_acting=True,
            is_liquidating=False,
            not_reported_last_year=True,
            not_in_same_registry=False,
            ceo_has_other_companies=True,
            negative_list_risk=False,
            bankruptcy_probability=5,
            bankruptcy_vars=None,
            is_enough_finance_data=True,
            relative_success=7,
            revenue_forecast=25000,
            assets_forecast=20000,
            dev_stage="Развивается активно",
            dev_stage_coordinates=None,
        )
        create_company(company)

        params = {
            "size": company.size,
            "region_codes": company.region_code,
            "is_acting": int(company.is_acting),
            "bankruptcy_probability": int(company.bankruptcy_probability),
            "is_liquidating": int(company.is_liquidating),
            "not_reported_last_year": int(company.not_reported_last_year),
            "not_in_same_registry": int(company.not_in_same_registry),
            "ceo_has_other_companies": int(company.ceo_has_other_companies),
            "negative_list_risk": int(company.negative_list_risk),
        }

        response = await client.get(self.url, params=params)
        assert response.status == HTTPStatus.OK

        assert await response.json() == {
            "data": [
                company.to_dict(),
            ],
            "message": "OK",
        }


class TestRegionsView:
    url = "/regions"

    async def test_request_with_non_empty_data(
            self,
            client: TestClient,
            create_company: Callable,
    ) -> None:
        regions = {
            "01": "Алтайский край",
            "03": "Краснодарский край",
            "04": "Красноярский край",
        }

        for i, (region_code, region_name) in enumerate(regions.items()):
            itn = region_code * 5
            psrn = f"{region_code * 6}{i}"

            company = Company(
                id=i,
                name="ЗАО ОКБ",
                size="Крупная",
                registered_at=date(2010, 1, 1),
                itn=itn,
                psrn=psrn,
                region_code=region_code,
                region_name=region_name,
                activity_code="5",
                activity_name="Высокая",
                charter_capital=1200,
                is_acting=True,
                is_liquidating=False,
                not_reported_last_year=True,
                not_in_same_registry=False,
                ceo_has_other_companies=True,
                negative_list_risk=False,
                bankruptcy_probability=5,
                bankruptcy_vars=None,
                is_enough_finance_data=True,
                relative_success=7,
                revenue_forecast=25000,
                assets_forecast=20000,
                dev_stage="Развивается активно",
                dev_stage_coordinates=None,
            )
            create_company(company)

        response = await client.get(self.url)

        assert await response.json() == {
            "data": regions,
            "message": "OK",
        }
