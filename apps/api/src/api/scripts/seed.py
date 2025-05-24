#!/usr/bin/env python3
"""
Setup script for OrchestrAI database initialization
"""
import asyncio
import sys
from pathlib import Path
from typing import Optional

from prisma import Prisma
from api.services.auth import AuthService

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))


async def setup_database():
    """Initialize the database with default data"""
    prisma = Prisma()
    auth_service = AuthService()

    try:
        print("Connecting to database...")
        await prisma.connect()
        await auth_service.prisma.connect()

        # Check if already initialized
        existing_tenant = await prisma.tenant.find_first()
        if existing_tenant:
            print("Database already initialized!")
            return

        print("Initializing database...")

        # Create default license
        print("Creating default license...")
        license = await prisma.license.create({
            "data": {"type": "FREE"}
        })

        # Create default tenant
        print("Creating default tenant...")
        tenant = await prisma.tenant.create({
            "data": {
                "name": "Default Organization",
                "slug": "default-org",
                "licenseId": license.id
            }
        })

        # Create default roles
        print("Creating default roles...")
        admin_role = await prisma.userrole.create({
            "data": {
                "name": "Business Admin",
                "type": "BUSINESS_ADMIN",
                "permissions": {
                    "projects": ["create", "read", "update", "delete"],
                    "agents": ["create", "read", "update", "delete"],
                    "users": ["create", "read", "update", "delete"],
                    "documents": ["create", "read", "update", "delete"]
                }
            }
        })

        await prisma.userrole.create({
            "data": {
                "name": "Customer User",
                "type": "CUSTOMER_USER",
                "permissions": {
                    "projects": ["read"],
                    "agents": ["read"],
                    "documents": ["read"]
                }
            }
        })

        # Create default admin user
        print("Creating default admin user...")
        await auth_service.register_user(
            email="admin@orchestrai.com",
            password="admin123!",  # Change this in production!
            tenant_id=tenant.id,
            first_name="Admin",
            last_name="User",
            role_id=admin_role.id
        )

        print("\nSetup completed successfully!")
        print("\nDefault credentials:")
        print("  Email: admin@orchestrai.com")
        print("  Password: admin123!")
        print(f"  Tenant ID: {tenant.id}")
        print(f"  Tenant Slug: {tenant.slug}")
        print("\n⚠️  IMPORTANT: Change the default password immediately!")

    except Exception as e:
        print(f"Setup failed: {str(e)}")
        raise
    finally:
        await prisma.disconnect()
        await auth_service.prisma.disconnect()


async def create_tenant(name: str, slug: str, license_type: str = "FREE"):
    """Create a new tenant"""
    prisma = Prisma()

    try:
        await prisma.connect()

        # Check if slug already exists
        existing = await prisma.tenant.find_first(
            where={"slug": slug}
        )
        if existing:
            print(f"Tenant with slug '{slug}' already exists!")
            return

        # Get or create license
        license = await prisma.license.find_first(
            where={"type": license_type}
        )
        if not license:
            license = await prisma.license.create({
                "data": {"type": license_type}
            })

        # Create tenant
        tenant = await prisma.tenant.create({
            "data": {
                "name": name,
                "slug": slug,
                "licenseId": license.id
            }
        })

        print("Tenant created successfully!")
        print(f"  ID: {tenant.id}")
        print(f"  Name: {tenant.name}")
        print(f"  Slug: {tenant.slug}")

    except Exception as e:
        print(f"Failed to create tenant: {str(e)}")
        raise
    finally:
        await prisma.disconnect()


async def create_user(
    email: str,
    password: str,
    tenant_id: str,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    role_type: str = "CUSTOMER_USER"
):
    """Create a new user"""
    prisma = Prisma()
    auth_service = AuthService()

    try:
        await prisma.connect()
        await auth_service.prisma.connect()

        # Verify tenant exists
        tenant = await prisma.tenant.find_unique(
            where={"id": tenant_id}
        )
        if not tenant:
            print(f"Tenant with ID '{tenant_id}' not found!")
            return

        # Get role
        role = await prisma.userrole.find_first(
            where={"type": role_type}
        )
        if not role:
            print(f"Role type '{role_type}' not found!")
            return

        # Create user
        result = await auth_service.register_user(
            email=email,
            password=password,
            tenant_id=tenant_id,
            first_name=first_name,
            last_name=last_name,
            role_id=role.id
        )

        print("User created successfully!")
        print(f"  ID: {result['user']['id']}")
        print(f"  Email: {result['user']['email']}")
        print(f"  Tenant: {tenant.name}")
        print(f"  Role: {role.name}")

    except Exception as e:
        print(f"Failed to create user: {str(e)}")
        raise
    finally:
        await prisma.disconnect()
        await auth_service.prisma.disconnect()


def main():
    """Main entry point for the setup script"""
    import argparse

    parser = argparse.ArgumentParser(description='OrchestrAI Database Setup')
    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Setup command
    subparsers.add_parser('init', help='Initialize database with defaults')

    # Create tenant command
    tenant_parser = subparsers.add_parser(
        'create-tenant',
        help='Create a new tenant'
    )
    tenant_parser.add_argument('--name', required=True, help='Tenant name')
    tenant_parser.add_argument(
        '--slug', required=True, help='Tenant slug (URL-friendly)')
    tenant_parser.add_argument(
        '--license',
        default='FREE',
        choices=['FREE', 'BASIC', 'PRO', 'ENTERPRISE', 'CUSTOM'],
        help='License type'
    )

    # Create user command
    user_parser = subparsers.add_parser(
        'create-user',
        help='Create a new user'
    )
    user_parser.add_argument('--email', required=True, help='User email')
    user_parser.add_argument('--password', required=True, help='User password')
    user_parser.add_argument('--tenant-id', required=True, help='Tenant ID')
    user_parser.add_argument('--first-name', help='First name')
    user_parser.add_argument('--last-name', help='Last name')
    user_parser.add_argument(
        '--role',
        default='CUSTOMER_USER',
        choices=[
            'BUSINESS_ADMIN',
            'BUSINESS_USER',
            'CUSTOMER_ADMIN',
            'CUSTOMER_USER'
        ],
        help='User role'
    )

    args = parser.parse_args()

    if args.command == 'init':
        asyncio.run(setup_database())
    elif args.command == 'create-tenant':
        asyncio.run(create_tenant(args.name, args.slug, args.license))
    elif args.command == 'create-user':
        asyncio.run(create_user(
            args.email,
            args.password,
            args.tenant_id,
            args.first_name,
            args.last_name,
            args.role
        ))
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
