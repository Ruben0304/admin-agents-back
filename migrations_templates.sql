-- Migration for Application and Assistant Templates
-- This migration adds support for dynamic template-based creation

-- Create application templates table
CREATE TABLE IF NOT EXISTS application_templates (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    display_name VARCHAR(150) NOT NULL,
    description TEXT,
    icon_url VARCHAR(255),
    category VARCHAR(50) DEFAULT 'general',
    tags JSON DEFAULT '[]'::json,
    template_config JSON DEFAULT '{}'::json,
    default_assistants JSON DEFAULT '[]'::json,
    usage_count INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Create indexes for application templates
CREATE INDEX IF NOT EXISTS idx_application_templates_category ON application_templates(category);
CREATE INDEX IF NOT EXISTS idx_application_templates_active ON application_templates(is_active);
CREATE INDEX IF NOT EXISTS idx_application_templates_name ON application_templates(name);

-- Create assistant templates table
CREATE TABLE IF NOT EXISTS assistant_templates (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    display_name VARCHAR(150) NOT NULL,
    description TEXT,
    category VARCHAR(50) DEFAULT 'general',
    system_prompt_template TEXT NOT NULL,
    default_provider VARCHAR(50),
    default_model VARCHAR(100),
    default_config JSON DEFAULT '{}'::json,
    tags JSON DEFAULT '[]'::json,
    prompt_variables JSON DEFAULT '[]'::json,
    usage_count INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Create indexes for assistant templates
CREATE INDEX IF NOT EXISTS idx_assistant_templates_category ON assistant_templates(category);
CREATE INDEX IF NOT EXISTS idx_assistant_templates_active ON assistant_templates(is_active);
CREATE INDEX IF NOT EXISTS idx_assistant_templates_name ON assistant_templates(name);

-- Insert some sample application templates
INSERT INTO application_templates (
    name, display_name, description, category, tags, template_config, default_assistants, created_by
) VALUES 
(
    'ecommerce_basic',
    'E-Commerce Básico',
    'Aplicación de comercio electrónico con asistentes para soporte al cliente y ventas',
    'ecommerce',
    '["commerce", "sales", "support"]'::json,
    '{"features": ["product_catalog", "order_management", "customer_support"], "theme": "modern"}'::json,
    '[
        {
            "name": "Customer Support",
            "description": "Asistente para soporte al cliente",
            "system_prompt": "Eres un asistente especializado en soporte al cliente para una tienda en línea. Tu trabajo es ayudar a los clientes con sus consultas sobre productos, pedidos, devoluciones y cualquier problema que puedan tener. Mantén un tono amigable y profesional.",
            "endpoint": "/support",
            "is_streaming": true,
            "config": {"max_tokens": 500, "temperature": 0.7}
        },
        {
            "name": "Sales Assistant",
            "description": "Asistente especializado en ventas",
            "system_prompt": "Eres un asistente especializado en ventas para una tienda en línea. Tu objetivo es ayudar a los clientes a encontrar los productos perfectos para sus necesidades, proporcionar recomendaciones personalizadas y guiarlos a través del proceso de compra. Sé persuasivo pero no agresivo.",
            "endpoint": "/sales",
            "is_streaming": false,
            "config": {"max_tokens": 800, "temperature": 0.6}
        }
    ]'::json,
    1
),
(
    'customer_support_center',
    'Centro de Soporte al Cliente',
    'Centro completo de soporte al cliente con múltiples especializaciones',
    'customer_support',
    '["support", "help", "service"]'::json,
    '{"languages": ["spanish", "english"], "availability": "24/7"}'::json,
    '[
        {
            "name": "General Support",
            "description": "Soporte general para consultas básicas",
            "system_prompt": "Eres un asistente de soporte general. Ayuda a los usuarios con consultas básicas, proporciona información sobre productos y servicios, y escalas casos complejos cuando sea necesario.",
            "endpoint": "/general-support",
            "is_streaming": true,
            "config": {"max_tokens": 600, "temperature": 0.5}
        },
        {
            "name": "Technical Support",
            "description": "Soporte técnico especializado",
            "system_prompt": "Eres un especialista en soporte técnico. Ayuda a los usuarios con problemas técnicos, guíalos a través de soluciones paso a paso, y proporciona información detallada sobre configuraciones y troubleshooting.",
            "endpoint": "/tech-support",
            "is_streaming": false,
            "config": {"max_tokens": 1000, "temperature": 0.3}
        }
    ]'::json,
    1
),
(
    'banking_app',
    'Aplicación Bancaria',
    'Sistema bancario con asistentes para gestión de cuentas y asesoría financiera',
    'banking',
    '["banking", "finance", "money"]'::json,
    '{"security": "high", "compliance": ["PCI", "SOX"]}'::json,
    '[
        {
            "name": "Account Manager",
            "description": "Gestor de cuentas personales",
            "system_prompt": "Eres un asistente bancario especializado en gestión de cuentas. Ayuda a los clientes con consultas sobre balances, transacciones, transferencias y servicios bancarios básicos. Mantén la seguridad y confidencialidad en todo momento.",
            "endpoint": "/account-manager",
            "is_streaming": false,
            "config": {"max_tokens": 400, "temperature": 0.2}
        },
        {
            "name": "Financial Advisor",
            "description": "Asesor financiero personal",
            "system_prompt": "Eres un asesor financiero especializado. Proporcionas consejos sobre inversiones, ahorros, planificación financiera y productos bancarios. Ofrece recomendaciones personalizadas basadas en las necesidades del cliente.",
            "endpoint": "/financial-advisor",
            "is_streaming": true,
            "config": {"max_tokens": 800, "temperature": 0.4}
        }
    ]'::json,
    1
);

-- Insert some sample assistant templates
INSERT INTO assistant_templates (
    name, display_name, description, category, system_prompt_template, 
    default_provider, default_model, default_config, tags, prompt_variables, created_by
) VALUES 
(
    'customer_support_general',
    'Soporte al Cliente General',
    'Asistente genérico para soporte al cliente que puede personalizarse por empresa',
    'customer_support',
    'Eres un asistente especializado en soporte al cliente para {company_name}. Tu trabajo es ayudar a los clientes con sus consultas sobre {product_type}, pedidos, devoluciones y cualquier problema que puedan tener. Mantén un tono {tone_style} y siempre representa los valores de {company_name}. {additional_instructions}',
    'gemini',
    'gemini-2.5-pro',
    '{"max_tokens": 500, "temperature": 0.7, "streaming": true}'::json,
    '["support", "customer", "general", "customizable"]'::json,
    '["company_name", "product_type", "tone_style", "additional_instructions"]'::json,
    1
),
(
    'sales_assistant',
    'Asistente de Ventas',
    'Asistente especializado en ventas con personalización por industria',
    'sales',
    'Eres un asistente especializado en ventas para {company_name} en la industria de {industry}. Tu objetivo es ayudar a los clientes a encontrar {product_category} perfectos para sus necesidades. Utiliza técnicas de venta {sales_approach} y siempre enfócate en {key_selling_points}. Tu meta es {sales_goal}.',
    'cohere',
    'command-r',
    '{"max_tokens": 800, "temperature": 0.6, "streaming": false}'::json,
    '["sales", "commerce", "industry", "customizable"]'::json,
    '["company_name", "industry", "product_category", "sales_approach", "key_selling_points", "sales_goal"]'::json,
    1
),
(
    'content_writer',
    'Escritor de Contenido',
    'Asistente para creación de contenido adaptable a diferentes estilos y audiencias',
    'content_writing',
    'Eres un escritor de contenido experto especializado en {content_type} para {target_audience}. Tu estilo de escritura es {writing_style} y siempres escribes en {language}. Tu especialidad incluye {content_specialty} y debes mantener un tono {brand_voice}. Siempre consideras {content_guidelines} en tu trabajo.',
    'gemini',
    'gemini-2.5-pro',
    '{"max_tokens": 1200, "temperature": 0.8, "streaming": true}'::json,
    '["content", "writing", "marketing", "creative"]'::json,
    '["content_type", "target_audience", "writing_style", "language", "content_specialty", "brand_voice", "content_guidelines"]'::json,
    1
),
(
    'data_analyst',
    'Analista de Datos',
    'Asistente especializado en análisis de datos y reporting',
    'data_analysis',
    'Eres un analista de datos experto trabajando para {company_name}. Te especializas en análisis de {data_type} usando herramientas como {tools_used}. Tu enfoque principal es {analysis_focus} y generas reportes en formato {report_format}. Siempre proporcionas insights {insight_level} y recomendaciones {recommendation_style}.',
    'cohere',
    'command-r',
    '{"max_tokens": 1000, "temperature": 0.3, "streaming": false}'::json,
    '["data", "analysis", "reporting", "business"]'::json,
    '["company_name", "data_type", "tools_used", "analysis_focus", "report_format", "insight_level", "recommendation_style"]'::json,
    1
),
(
    'educational_tutor',
    'Tutor Educativo',
    'Asistente educativo personalizable para diferentes materias y niveles',
    'education',
    'Eres un tutor educativo especializado en {subject_area} para estudiantes de nivel {education_level}. Tu método de enseñanza es {teaching_method} y siempre adaptas tu explicación al {learning_style} del estudiante. Te enfocas en {learning_objectives} y utilizas {teaching_resources} para mejorar el aprendizaje. Tu objetivo es {educational_goal}.',
    'gemini',
    'gemini-2.5-pro',
    '{"max_tokens": 800, "temperature": 0.5, "streaming": true}'::json,
    '["education", "tutoring", "learning", "academic"]'::json,
    '["subject_area", "education_level", "teaching_method", "learning_style", "learning_objectives", "teaching_resources", "educational_goal"]'::json,
    1
);

-- Add update triggers for both tables
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_application_templates_updated_at 
    BEFORE UPDATE ON application_templates 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_assistant_templates_updated_at 
    BEFORE UPDATE ON assistant_templates 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Grant permissions (adjust according to your user setup)
-- GRANT ALL PRIVILEGES ON application_templates TO your_app_user;
-- GRANT ALL PRIVILEGES ON assistant_templates TO your_app_user;
-- GRANT USAGE, SELECT ON SEQUENCE application_templates_id_seq TO your_app_user;
-- GRANT USAGE, SELECT ON SEQUENCE assistant_templates_id_seq TO your_app_user;