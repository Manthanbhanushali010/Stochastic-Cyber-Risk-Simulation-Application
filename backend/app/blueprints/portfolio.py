"""
Portfolio blueprint for managing insurance portfolios and policies.

This module provides endpoints for creating, updating, and managing
insurance portfolios and their associated policies.
"""

from datetime import datetime, timezone
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import Schema, fields, ValidationError, validates
import structlog

from app import db
from app.models import User, Portfolio, Policy

logger = structlog.get_logger(__name__)

# Create the portfolio blueprint
portfolio_bp = Blueprint('portfolio', __name__)


# Validation schemas
class PolicySchema(Schema):
    """Schema for policy validation."""
    
    policy_number = fields.Str(required=True, validate=lambda x: len(x.strip()) > 0)
    policyholder_name = fields.Str(required=True, validate=lambda x: len(x.strip()) > 0)
    coverage_type = fields.Str(required=True, validate=lambda x: x in ['cyber_liability', 'data_breach', 'business_interruption', 'errors_omissions'])
    coverage_limit = fields.Float(required=True, validate=lambda x: x > 0)
    deductible = fields.Float(missing=0.0, validate=lambda x: x >= 0)
    sub_limits = fields.Dict(missing=dict)
    annual_premium = fields.Float(missing=None, allow_none=True, validate=lambda x: x is None or x >= 0)
    policy_start_date = fields.DateTime(required=True)
    policy_end_date = fields.DateTime(required=True)
    industry_sector = fields.Str(missing=None, allow_none=True)
    company_size = fields.Str(missing=None, allow_none=True, validate=lambda x: x is None or x in ['small', 'medium', 'large', 'enterprise'])
    risk_score = fields.Float(missing=None, allow_none=True, validate=lambda x: x is None or 0 <= x <= 10)
    country = fields.Str(missing=None, allow_none=True, validate=lambda x: x is None or len(x) == 2)
    region = fields.Str(missing=None, allow_none=True)
    attributes = fields.Dict(missing=dict)
    
    @validates('policy_end_date')
    def validate_policy_dates(self, value):
        """Validate that policy end date is after start date."""
        # This will be validated in the route handler where we have both dates
        pass


class PortfolioSchema(Schema):
    """Schema for portfolio validation."""
    
    name = fields.Str(required=True, validate=lambda x: len(x.strip()) > 0)
    description = fields.Str(missing="")
    configuration = fields.Dict(missing=dict)


class PortfolioUpdateSchema(Schema):
    """Schema for portfolio update validation."""
    
    name = fields.Str(missing=None, validate=lambda x: x is None or len(x.strip()) > 0)
    description = fields.Str(missing=None)
    configuration = fields.Dict(missing=None)


# Initialize schemas
policy_schema = PolicySchema()
portfolio_schema = PortfolioSchema()
portfolio_update_schema = PortfolioUpdateSchema()


@portfolio_bp.route('/', methods=['POST'])
@jwt_required()
def create_portfolio():
    """
    Create a new insurance portfolio.
    
    Expected JSON payload:
    {
        "name": "Portfolio Name",
        "description": "Portfolio description",
        "configuration": {}
    }
    """
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Validate request data
        json_data = request.get_json()
        if not json_data:
            return jsonify({'error': 'No data provided'}), 400
        
        try:
            validated_data = portfolio_schema.load(json_data)
        except ValidationError as err:
            return jsonify({'error': 'Validation failed', 'details': err.messages}), 400
        
        # Check for duplicate portfolio names
        existing_portfolio = Portfolio.query.filter_by(
            user_id=current_user_id,
            name=validated_data['name']
        ).first()
        
        if existing_portfolio:
            return jsonify({'error': 'Portfolio with this name already exists'}), 409
        
        # Create new portfolio
        portfolio = Portfolio(
            user_id=current_user_id,
            name=validated_data['name'],
            description=validated_data.get('description', ''),
            configuration=validated_data.get('configuration', {})
        )
        
        db.session.add(portfolio)
        db.session.commit()
        
        logger.info("Portfolio created", portfolio_id=str(portfolio.id), user_id=current_user_id)
        
        return jsonify({
            'message': 'Portfolio created successfully',
            'portfolio': portfolio.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error("Failed to create portfolio", error=str(e))
        return jsonify({'error': 'Failed to create portfolio', 'message': str(e)}), 500


@portfolio_bp.route('/', methods=['GET'])
@jwt_required()
def list_portfolios():
    """
    List user's portfolios with optional filtering.
    
    Query parameters:
    - limit: Maximum number of results (default: 50)
    - offset: Number of results to skip (default: 0)
    """
    try:
        current_user_id = get_jwt_identity()
        
        # Get query parameters
        limit = min(int(request.args.get('limit', 50)), 100)  # Max 100 results
        offset = int(request.args.get('offset', 0))
        
        # Build query
        query = Portfolio.query.filter_by(user_id=current_user_id)
        query = query.order_by(Portfolio.created_at.desc())
        
        total_count = query.count()
        portfolios = query.offset(offset).limit(limit).all()
        
        return jsonify({
            'portfolios': [portfolio.to_dict() for portfolio in portfolios],
            'total_count': total_count,
            'limit': limit,
            'offset': offset,
            'has_more': (offset + limit) < total_count
        }), 200
        
    except Exception as e:
        logger.error("Failed to list portfolios", error=str(e))
        return jsonify({'error': 'Failed to retrieve portfolios'}), 500


@portfolio_bp.route('/<portfolio_id>', methods=['GET'])
@jwt_required()
def get_portfolio(portfolio_id: str):
    """Get detailed information about a specific portfolio."""
    try:
        current_user_id = get_jwt_identity()
        
        portfolio = Portfolio.query.filter_by(
            id=portfolio_id,
            user_id=current_user_id
        ).first()
        
        if not portfolio:
            return jsonify({'error': 'Portfolio not found'}), 404
        
        # Include policy information
        result = portfolio.to_dict()
        result['policies'] = [policy.to_dict() for policy in portfolio.policies]
        
        return jsonify({'portfolio': result}), 200
        
    except Exception as e:
        logger.error("Failed to get portfolio", error=str(e))
        return jsonify({'error': 'Failed to retrieve portfolio'}), 500


@portfolio_bp.route('/<portfolio_id>', methods=['PUT'])
@jwt_required()
def update_portfolio(portfolio_id: str):
    """
    Update a portfolio.
    
    Expected JSON payload (all fields optional):
    {
        "name": "Updated Portfolio Name",
        "description": "Updated description",
        "configuration": {}
    }
    """
    try:
        current_user_id = get_jwt_identity()
        
        portfolio = Portfolio.query.filter_by(
            id=portfolio_id,
            user_id=current_user_id
        ).first()
        
        if not portfolio:
            return jsonify({'error': 'Portfolio not found'}), 404
        
        # Validate request data
        json_data = request.get_json()
        if not json_data:
            return jsonify({'error': 'No data provided'}), 400
        
        try:
            validated_data = portfolio_update_schema.load(json_data)
        except ValidationError as err:
            return jsonify({'error': 'Validation failed', 'details': err.messages}), 400
        
        # Check for duplicate portfolio names if name is being changed
        if 'name' in validated_data and validated_data['name'] != portfolio.name:
            existing_portfolio = Portfolio.query.filter_by(
                user_id=current_user_id,
                name=validated_data['name']
            ).first()
            
            if existing_portfolio:
                return jsonify({'error': 'Portfolio with this name already exists'}), 409
        
        # Update portfolio fields
        if 'name' in validated_data:
            portfolio.name = validated_data['name']
        if 'description' in validated_data:
            portfolio.description = validated_data['description']
        if 'configuration' in validated_data:
            portfolio.configuration = validated_data['configuration']
        
        portfolio.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        
        logger.info("Portfolio updated", portfolio_id=str(portfolio.id), user_id=current_user_id)
        
        return jsonify({
            'message': 'Portfolio updated successfully',
            'portfolio': portfolio.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error("Failed to update portfolio", error=str(e))
        return jsonify({'error': 'Failed to update portfolio'}), 500


@portfolio_bp.route('/<portfolio_id>', methods=['DELETE'])
@jwt_required()
def delete_portfolio(portfolio_id: str):
    """Delete a portfolio and all its policies."""
    try:
        current_user_id = get_jwt_identity()
        
        portfolio = Portfolio.query.filter_by(
            id=portfolio_id,
            user_id=current_user_id
        ).first()
        
        if not portfolio:
            return jsonify({'error': 'Portfolio not found'}), 404
        
        # Check if portfolio is used in any simulations
        simulation_count = portfolio.simulation_runs.count()
        if simulation_count > 0:
            return jsonify({
                'error': 'Cannot delete portfolio',
                'message': f'Portfolio is used in {simulation_count} simulation(s)'
            }), 409
        
        # Delete portfolio (cascade will handle policies)
        db.session.delete(portfolio)
        db.session.commit()
        
        logger.info("Portfolio deleted", portfolio_id=portfolio_id, user_id=current_user_id)
        
        return jsonify({'message': 'Portfolio deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error("Failed to delete portfolio", error=str(e))
        return jsonify({'error': 'Failed to delete portfolio'}), 500


@portfolio_bp.route('/<portfolio_id>/policies', methods=['POST'])
@jwt_required()
def add_policy_to_portfolio(portfolio_id: str):
    """
    Add a new policy to a portfolio.
    
    Expected JSON payload:
    {
        "policy_number": "POL-123456",
        "policyholder_name": "Company ABC",
        "coverage_type": "cyber_liability",
        "coverage_limit": 1000000,
        "deductible": 10000,
        "policy_start_date": "2024-01-01T00:00:00Z",
        "policy_end_date": "2024-12-31T23:59:59Z",
        "industry_sector": "technology",
        "company_size": "medium"
    }
    """
    try:
        current_user_id = get_jwt_identity()
        
        portfolio = Portfolio.query.filter_by(
            id=portfolio_id,
            user_id=current_user_id
        ).first()
        
        if not portfolio:
            return jsonify({'error': 'Portfolio not found'}), 404
        
        # Validate request data
        json_data = request.get_json()
        if not json_data:
            return jsonify({'error': 'No data provided'}), 400
        
        try:
            validated_data = policy_schema.load(json_data)
        except ValidationError as err:
            return jsonify({'error': 'Validation failed', 'details': err.messages}), 400
        
        # Validate policy dates
        if validated_data['policy_end_date'] <= validated_data['policy_start_date']:
            return jsonify({'error': 'Policy end date must be after start date'}), 400
        
        # Check for duplicate policy numbers within the portfolio
        existing_policy = Policy.query.filter_by(
            portfolio_id=portfolio_id,
            policy_number=validated_data['policy_number']
        ).first()
        
        if existing_policy:
            return jsonify({'error': 'Policy with this number already exists in portfolio'}), 409
        
        # Create new policy
        policy = Policy(
            portfolio_id=portfolio_id,
            policy_number=validated_data['policy_number'],
            policyholder_name=validated_data['policyholder_name'],
            coverage_type=validated_data['coverage_type'],
            coverage_limit=validated_data['coverage_limit'],
            deductible=validated_data.get('deductible', 0.0),
            sub_limits=validated_data.get('sub_limits', {}),
            annual_premium=validated_data.get('annual_premium'),
            policy_start_date=validated_data['policy_start_date'],
            policy_end_date=validated_data['policy_end_date'],
            industry_sector=validated_data.get('industry_sector'),
            company_size=validated_data.get('company_size'),
            risk_score=validated_data.get('risk_score'),
            country=validated_data.get('country'),
            region=validated_data.get('region'),
            attributes=validated_data.get('attributes', {})
        )
        
        db.session.add(policy)
        db.session.commit()
        
        logger.info("Policy added to portfolio", policy_id=str(policy.id), portfolio_id=portfolio_id)
        
        return jsonify({
            'message': 'Policy added successfully',
            'policy': policy.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error("Failed to add policy", error=str(e))
        return jsonify({'error': 'Failed to add policy', 'message': str(e)}), 500


@portfolio_bp.route('/<portfolio_id>/policies/<policy_id>', methods=['PUT'])
@jwt_required()
def update_policy(portfolio_id: str, policy_id: str):
    """Update a policy within a portfolio."""
    try:
        current_user_id = get_jwt_identity()
        
        # Verify portfolio ownership
        portfolio = Portfolio.query.filter_by(
            id=portfolio_id,
            user_id=current_user_id
        ).first()
        
        if not portfolio:
            return jsonify({'error': 'Portfolio not found'}), 404
        
        # Get the policy
        policy = Policy.query.filter_by(
            id=policy_id,
            portfolio_id=portfolio_id
        ).first()
        
        if not policy:
            return jsonify({'error': 'Policy not found'}), 404
        
        # Validate request data
        json_data = request.get_json()
        if not json_data:
            return jsonify({'error': 'No data provided'}), 400
        
        try:
            validated_data = policy_schema.load(json_data)
        except ValidationError as err:
            return jsonify({'error': 'Validation failed', 'details': err.messages}), 400
        
        # Validate policy dates
        if validated_data['policy_end_date'] <= validated_data['policy_start_date']:
            return jsonify({'error': 'Policy end date must be after start date'}), 400
        
        # Check for duplicate policy numbers if policy number is being changed
        if validated_data['policy_number'] != policy.policy_number:
            existing_policy = Policy.query.filter_by(
                portfolio_id=portfolio_id,
                policy_number=validated_data['policy_number']
            ).first()
            
            if existing_policy:
                return jsonify({'error': 'Policy with this number already exists in portfolio'}), 409
        
        # Update policy fields
        policy.policy_number = validated_data['policy_number']
        policy.policyholder_name = validated_data['policyholder_name']
        policy.coverage_type = validated_data['coverage_type']
        policy.coverage_limit = validated_data['coverage_limit']
        policy.deductible = validated_data.get('deductible', 0.0)
        policy.sub_limits = validated_data.get('sub_limits', {})
        policy.annual_premium = validated_data.get('annual_premium')
        policy.policy_start_date = validated_data['policy_start_date']
        policy.policy_end_date = validated_data['policy_end_date']
        policy.industry_sector = validated_data.get('industry_sector')
        policy.company_size = validated_data.get('company_size')
        policy.risk_score = validated_data.get('risk_score')
        policy.country = validated_data.get('country')
        policy.region = validated_data.get('region')
        policy.attributes = validated_data.get('attributes', {})
        policy.updated_at = datetime.now(timezone.utc)
        
        db.session.commit()
        
        logger.info("Policy updated", policy_id=policy_id, portfolio_id=portfolio_id)
        
        return jsonify({
            'message': 'Policy updated successfully',
            'policy': policy.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error("Failed to update policy", error=str(e))
        return jsonify({'error': 'Failed to update policy'}), 500


@portfolio_bp.route('/<portfolio_id>/policies/<policy_id>', methods=['DELETE'])
@jwt_required()
def delete_policy(portfolio_id: str, policy_id: str):
    """Delete a policy from a portfolio."""
    try:
        current_user_id = get_jwt_identity()
        
        # Verify portfolio ownership
        portfolio = Portfolio.query.filter_by(
            id=portfolio_id,
            user_id=current_user_id
        ).first()
        
        if not portfolio:
            return jsonify({'error': 'Portfolio not found'}), 404
        
        # Get the policy
        policy = Policy.query.filter_by(
            id=policy_id,
            portfolio_id=portfolio_id
        ).first()
        
        if not policy:
            return jsonify({'error': 'Policy not found'}), 404
        
        # Delete policy
        db.session.delete(policy)
        db.session.commit()
        
        logger.info("Policy deleted", policy_id=policy_id, portfolio_id=portfolio_id)
        
        return jsonify({'message': 'Policy deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error("Failed to delete policy", error=str(e))
        return jsonify({'error': 'Failed to delete policy'}), 500


@portfolio_bp.route('/<portfolio_id>/summary', methods=['GET'])
@jwt_required()
def get_portfolio_summary(portfolio_id: str):
    """Get summary statistics for a portfolio."""
    try:
        current_user_id = get_jwt_identity()
        
        portfolio = Portfolio.query.filter_by(
            id=portfolio_id,
            user_id=current_user_id
        ).first()
        
        if not portfolio:
            return jsonify({'error': 'Portfolio not found'}), 404
        
        policies = portfolio.policies.all()
        
        if not policies:
            return jsonify({
                'portfolio_id': portfolio_id,
                'summary': {
                    'total_policies': 0,
                    'total_coverage_limit': 0,
                    'total_premium': 0,
                    'average_deductible': 0,
                    'coverage_types': {},
                    'company_sizes': {},
                    'industry_sectors': {}
                }
            }), 200
        
        # Calculate summary statistics
        total_coverage = sum(policy.coverage_limit for policy in policies)
        total_premium = sum(policy.annual_premium or 0 for policy in policies)
        average_deductible = sum(policy.deductible for policy in policies) / len(policies)
        
        # Group by various attributes
        coverage_types = {}
        company_sizes = {}
        industry_sectors = {}
        
        for policy in policies:
            # Coverage types
            coverage_type = policy.coverage_type
            coverage_types[coverage_type] = coverage_types.get(coverage_type, 0) + 1
            
            # Company sizes
            if policy.company_size:
                company_size = policy.company_size
                company_sizes[company_size] = company_sizes.get(company_size, 0) + 1
            
            # Industry sectors
            if policy.industry_sector:
                sector = policy.industry_sector
                industry_sectors[sector] = industry_sectors.get(sector, 0) + 1
        
        return jsonify({
            'portfolio_id': portfolio_id,
            'summary': {
                'total_policies': len(policies),
                'total_coverage_limit': total_coverage,
                'total_premium': total_premium,
                'average_deductible': average_deductible,
                'coverage_types': coverage_types,
                'company_sizes': company_sizes,
                'industry_sectors': industry_sectors
            }
        }), 200
        
    except Exception as e:
        logger.error("Failed to get portfolio summary", error=str(e))
        return jsonify({'error': 'Failed to retrieve portfolio summary'}), 500 