from graceful.errors import DeserializationError
from graceful.serializers import BaseSerializer, _source
from zopsm.lib.rest.fields import ZopsDatetimeField, ZopsBooleanField, ZopsStringField


class ZopsBaseSerializer(BaseSerializer):
    def validate(self, object_dict, partial=False):
        """Validate given internal object returned by ``to_representation()``.

                Internal object is validated against missing/forbidden/invalid fields
                values using fields definitions defined in serializer.

                Args:
                    object_dict (dict): internal object dictionart to perform
                      to validate
                    partial (bool): if set to True then incomplete object_dict
                      is accepter and will not raise any exceptions when one
                      of fields is missing

                Raises:
                    DeserializationError:

                """

        sources_to_field_names = {
            _source(name, field): name
            for name, field in self.fields.items()
            }

        def _(names):
            if isinstance(names, list):
                return [
                    sources_to_field_names.get(name, name)
                    for name in names
                    ]
            elif isinstance(names, dict):
                return {
                    sources_to_field_names.get(name, name): value
                    for name, value in names.items()
                    }
            else:
                return names  # pragma: nocover

        # we are working on object_dict not an representation so there
        # is a need to annotate sources differently
        sources = {
            _source(name, field): field
            for name, field in self.fields.items()
            }

        # note: we are checking for all mising and invalid fields so we can
        # return exception with all fields that are missing and should
        # exist instead of single one
        missing = [
            name for name, field in sources.items()
            if all((not partial, name not in object_dict, not field.read_only))
            ]

        if missing:
            raise DeserializationError(missing=_(missing))

        forbidden = [
            name for name in object_dict
            if any((name not in sources, sources[name].read_only))
            ]

        if forbidden:
            raise DeserializationError(forbidden=_(forbidden))

        invalid = {}
        for name, value in object_dict.items():
            try:
                field = sources[name]

                if field.many:
                    for single_value in value:
                        field.validate(single_value)
                else:
                    field.validate(value)

            except ValueError as err:
                invalid[name] = str(err)

        if invalid:
            raise DeserializationError(invalid=_(invalid))


class ZopsBaseDBSerializer(ZopsBaseSerializer):
    creationTime = ZopsDatetimeField(
        "timestamp, auto field, default now(), first creation time of record", read_only=True,
        source='creation_time')
    lastUpdateTime = ZopsDatetimeField(
        "timestamp, auto field, default now(), last update time of record", read_only=True,
        source='last_update_time')
    isDeleted = ZopsBooleanField(
        "boolean, auto field, default false, indicates is record deleted or not", read_only=True,
        source='is_deleted')
    isActive = ZopsBooleanField(
        "boolean, auto field, default false, indicates is record deleted or not", read_only=True,
        source='is_active')
    trackingId = ZopsStringField(
        "Id number to track non-blocking operations' erroneous responses coming through web socket",
        read_only=True,
        source='tracking_id'
    )
