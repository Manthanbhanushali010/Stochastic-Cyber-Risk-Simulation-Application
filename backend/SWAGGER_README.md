# 📚 **Swagger/OpenAPI Documentation**

## 🎯 **Overview**

Your **Stochastic Cyber Risk Simulation Application** now includes comprehensive **Swagger/OpenAPI documentation** powered by **Flask-RESTX**. This provides interactive API documentation, request/response validation, and a testing interface.

---

## 🚀 **Features Added**

### **📖 Interactive Documentation**
- **Swagger UI Interface**: Browse all API endpoints with detailed descriptions
- **Request/Response Schemas**: Complete data models for all endpoints
- **Authentication Integration**: JWT Bearer token support built-in
- **Try It Out**: Test API endpoints directly from the browser

### **🔧 API Schema Validation**
- **Automatic Validation**: Request payloads validated against defined schemas
- **Error Responses**: Consistent error handling with detailed messages
- **Type Safety**: Strong typing for all API parameters and responses

### **📋 Comprehensive Coverage**
- **Authentication**: Login, register, profile management, password changes
- **Simulation**: Monte Carlo simulation configuration and execution
- **Portfolio**: Portfolio and policy management operations
- **Scenarios**: Risk scenario creation and comparison tools  
- **System**: Health checks, statistics, and system information

---

## 🌐 **Accessing Swagger Documentation**

### **Development Server**
```bash
# Start the development server
cd backend
python app.py

# Or using Flask CLI
export FLASK_APP=app.py
export FLASK_ENV=development
flask run
```

### **Access Points**
- **Swagger UI**: `http://localhost:5000/docs/`
- **OpenAPI JSON**: `http://localhost:5000/swagger.json`
- **Health Check**: `http://localhost:5000/health`

---

## 🔑 **Authentication in Swagger**

### **Getting Started**
1. **Register or Login** using the `/api/auth/register` or `/api/auth/login` endpoints
2. **Copy the JWT token** from the response
3. **Click "Authorize"** button at the top of Swagger UI
4. **Enter**: `Bearer <your-jwt-token>`
5. **Use authenticated endpoints** with automatic token inclusion

### **JWT Token Format**
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

---

## 📊 **API Endpoints Structure**

### **🔐 Authentication (`/api/auth`)**
- `POST /register` - Register new user account
- `POST /login` - Authenticate and receive JWT tokens
- `POST /refresh` - Refresh JWT access token
- `POST /logout` - Logout and invalidate tokens
- `GET /profile` - Get current user profile
- `PUT /profile` - Update user profile
- `POST /change-password` - Change user password

### **🎯 Simulation (`/api/simulation`)**
- `POST /run` - Start new Monte Carlo simulation
- `GET /list` - List user simulations with pagination
- `GET /{id}` - Get simulation details by ID
- `DELETE /{id}` - Delete simulation by ID
- `GET /{id}/results` - Get detailed simulation results
- `POST /{id}/stop` - Stop running simulation
- `GET /distributions` - Get available probability distributions

### **💼 Portfolio (`/api/portfolio`)**
- `GET /` - List user portfolios
- `POST /` - Create new portfolio
- `GET /{id}` - Get portfolio details
- `PUT /{id}` - Update portfolio
- `DELETE /{id}` - Delete portfolio
- `GET /{id}/policies` - Get portfolio policies
- `POST /{id}/policies` - Add policy to portfolio
- `GET /{id}/summary` - Get portfolio summary with metrics

### **📋 Scenarios (`/api/scenarios`)**
- `GET /` - List risk scenarios with filtering
- `POST /` - Create new risk scenario
- `GET /{id}` - Get scenario details
- `PUT /{id}` - Update scenario
- `DELETE /{id}` - Delete scenario
- `POST /compare` - Compare multiple scenarios

### **⚙️ System (`/api/system`)**
- `GET /health` - System health check
- `GET /info` - System information
- `GET /stats` - Usage statistics (authenticated)

---

## 🏗️ **Technical Implementation**

### **Flask-RESTX Integration**
```python
# API initialization with comprehensive documentation
api = Api(
    app,
    version='1.0.0',
    title='Stochastic Cyber Risk Simulation API',
    description='Enterprise-grade Monte Carlo cyber risk simulation',
    doc='/docs/',
    authorizations={'Bearer': {'type': 'apiKey', 'in': 'header', 'name': 'Authorization'}},
    security='Bearer'
)
```

### **Schema Definition Example**
```python
# Simulation parameters model
simulation_parameters_model = api.model('SimulationParameters', {
    'name': fields.String(required=True, description='Simulation name'),
    'iterations': fields.Integer(required=True, min=1000, max=100000),
    'event_parameters': fields.Nested(event_parameters_model),
    'portfolio': fields.Nested(portfolio_model)
})
```

### **Endpoint Documentation Example**
```python
@ns.route('/run')
class RunSimulationResource(Resource):
    @ns.doc('run_simulation', description='Start Monte Carlo simulation')
    @ns.expect(simulation_parameters_model, validate=True)
    @ns.response(202, 'Simulation started', simulation_run_model)
    @ns.response(400, 'Validation error', validation_error_model)
    @jwt_required()
    def post(self):
        return run_simulation()
```

---

## 🎨 **Swagger UI Features**

### **Interactive Testing**
- **Try It Out**: Execute API calls directly from the browser
- **Parameter Input**: Form-based parameter entry with validation
- **Response Preview**: View actual API responses with syntax highlighting
- **curl Commands**: Generated curl commands for each request

### **Schema Explorer**
- **Model Definitions**: Browse all data models with field descriptions
- **Nested Objects**: Expandable nested object schemas
- **Validation Rules**: Min/max values, required fields, data types
- **Example Values**: Sample data for all models

### **Documentation Features**
- **Endpoint Grouping**: Organized by functional areas (Auth, Simulation, etc.)
- **HTTP Methods**: Clear indication of GET, POST, PUT, DELETE operations
- **Status Codes**: Detailed response code explanations
- **Error Handling**: Comprehensive error response documentation

---

## 🔧 **Development Workflow**

### **Adding New Endpoints**
1. **Define API Models** in `api_schemas.py`
2. **Create Namespace** in `api_routes.py`
3. **Document Endpoints** with `@ns.doc()` decorators
4. **Add Validation** with `@ns.expect()` and `@ns.response()`
5. **Test via Swagger UI**

### **Schema Updates**
```python
# Update existing model
user_model = api.model('User', {
    'id': fields.String(description='User ID'),
    'email': fields.String(required=True, description='Email address'),
    'created_at': fields.DateTime(description='Account creation date')
})
```

### **Error Handling**
```python
# Consistent error responses
@ns.response(400, 'Validation error', validation_error_model)
@ns.response(401, 'Authentication required', error_model)
@ns.response(404, 'Resource not found', error_model)
```

---

## 📈 **Production Considerations**

### **Security**
- **JWT Authentication**: Secure token-based authentication
- **Input Validation**: All request payloads validated
- **CORS Configuration**: Properly configured cross-origin requests
- **Rate Limiting**: Ready for rate limiting implementation

### **Performance**
- **Schema Caching**: API schemas cached for performance
- **Lazy Loading**: Documentation loaded on-demand
- **Compression**: Response compression for large schemas

### **Monitoring**
- **Request Logging**: All API requests logged with structured logging
- **Error Tracking**: Comprehensive error handling and reporting
- **Health Checks**: Built-in health monitoring endpoints

---

## 🎯 **Benefits for Development**

### **Developer Experience**
- **Self-Documenting API**: Always up-to-date documentation
- **Interactive Testing**: No need for external tools like Postman
- **Schema Validation**: Catch errors early in development
- **Type Safety**: Clear contracts between frontend and backend

### **Client Integration**
- **OpenAPI Spec**: Generate client SDKs in any language
- **Contract Testing**: Validate API contracts automatically
- **Mock Servers**: Generate mock servers from OpenAPI spec
- **API Versioning**: Support for API version management

### **Testing Benefits**
- **Integration Testing**: Test API endpoints with real schemas
- **Documentation Testing**: Ensure docs match implementation
- **Regression Prevention**: Schema changes detected automatically
- **Quality Assurance**: Consistent API behavior validation

---

## 📝 **Next Steps**

### **Immediate Use**
1. **Start the server**: `python app.py`
2. **Open Swagger UI**: Visit `http://localhost:5000/docs/`
3. **Register/Login**: Create account and get JWT token
4. **Test endpoints**: Use "Try it out" feature
5. **Integrate frontend**: Use documented APIs for frontend development

### **Advanced Features**
- **API Versioning**: Implement versioned endpoints
- **Rate Limiting**: Add request rate limiting
- **Webhook Documentation**: Document webhook endpoints
- **SDK Generation**: Generate client libraries
- **API Testing**: Automated API contract testing

---

## 🎉 **Summary**

Your application now features **enterprise-grade API documentation** with:

✅ **Interactive Swagger UI** at `/docs/`  
✅ **Complete schema validation** for all endpoints  
✅ **JWT authentication integration**  
✅ **Production-ready error handling**  
✅ **Comprehensive endpoint coverage**  
✅ **Developer-friendly testing interface**  

The API documentation is now a **living document** that stays synchronized with your code, providing a professional interface for development, testing, and integration! 🚀 