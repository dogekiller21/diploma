from uuid import UUID

from app.db.base.storage import BaseStorage
from app.models.controller import (
    ControllerCreateModel,
    ControllerDataModel,
    SingleBlockControllerResponseModel,
)
from app.models.response import BlockControllerResponseModel
from app.models.versions import VersionCreateModel, VersionDataModel


class VersionStorage(BaseStorage):
    async def create_version_object(
        self,
        data: VersionCreateModel,
    ) -> VersionDataModel:
        query = """
            CREATE
            (vv:Version {id: randomUUID(), version: $version, data: $data, release_date: $release_date})
            RETURN vv.id AS id
        """
        result = await self.make_request(
            query=query,
            **data.dict(),
        )
        record = await result.single()
        record_data = record.data()
        record_data.update(data.dict())
        del record_data["data"]  # слишком длинная, пусть посидит
        return VersionDataModel.model_validate(record_data)

    async def get_version_data(self, version_id: str) -> VersionDataModel | None:
        result = await self.make_request(
            query="MATCH (vv:Version) WHERE vv.id = $version_id RETURN vv",
            version_id=version_id,
        )
        data = await result.data()
        if not data:
            return None
        return VersionDataModel.model_validate(data[0].get("vv"))

    async def get_controller_versions_response(
        self, limit: int, offset: int, controller_id: str | None = None
    ) -> SingleBlockControllerResponseModel | None:
        """
        [
            {
                'controller_name': 'controller1',
                'id': 'uuid',
                'block': {
                        'block_name': 'block1',
                        'model_name': 'model1',
                        'id': 'uuid'
                    },
                    'first_version': {
                        'version': '0.2b',
                        'id': 'uuid',
                        'release_date': '2024-02-01'
                    },
                    'versions': [
                        'version': '0.1b',
                        'id': 'uuid',
                        'release_date': '2023-02-01'
                    ],
                    'cars_count': 0
            }
        ]


        :param limit:
        :param offset:
        :param controller_id:
        :return:
        """

        db_query = """
            MATCH (cc:Controller)-[:LINKED_BLOCK]->(bb:Block)
            WHERE cc.id = $controller_id
            MATCH (vv:Version)<-[:LINKED_VERSION]-(cc)
            OPTIONAL MATCH (car:Car)-[:LINKED_CAR]->(bb)
            WITH cc, bb, collect(DISTINCT vv) as all_versions, count(DISTINCT car) as cars_count
            UNWIND all_versions as v
            WITH cc, bb, v, cars_count
            ORDER BY v.release_date DESC
            WITH cc, bb, cars_count, collect(v)[0..] as sorted_versions
            WITH cc, bb, cars_count, sorted_versions, range($offset, $offset + $limit - 1) as range
            UNWIND range as idx
            WITH cc, bb, cars_count, sorted_versions[idx] as version, idx
            WITH cc, bb, cars_count, collect(version) as limited_versions
            RETURN
                cc.controller_name as controller_name,
                cc.id as id,
                bb as block,
                limited_versions[0] as first_version,
                limited_versions[1..] as versions,
                cars_count
        """

        result = await self.make_request(
            query=db_query, limit=limit, offset=offset, controller_id=controller_id
        )
        data = await result.single()
        if not data:
            return None
        return SingleBlockControllerResponseModel.model_validate(data.data())
