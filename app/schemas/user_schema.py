from marshmallow import Schema, fields, validate

class UserRegisterSchema(Schema):
    username = fields.String(required=True, validate=validate.Length(min=1))
    email = fields.Email(required=True)
    password = fields.String(required=True, validate=validate.Length(min=6))

class UserLoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True)

class PasswordResetRequestSchema(Schema):
    email = fields.Email(required=True)

class PasswordResetSchema(Schema):
    password = fields.String(required=True, validate=validate.Length(min=6))

class UserBaseSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.String(dump_only=True)
    email = fields.Email(dump_only=True)
    is_admin = fields.Boolean(dump_only=True)
