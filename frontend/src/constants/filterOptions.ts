/** SHL catalog filter options (aligned with backend catalog filters). */
export const FILTER_OPTIONS = {
  job_family: [
    'Business', 'Clerical', 'Contact Center', 'Customer Service',
    'Information Technology', 'Safety', 'Sales',
  ],
  job_level: [
    'Director', 'Entry-Level', 'Executive', 'Front Line Manager',
    'General Population', 'Graduate', 'Manager', 'Mid-Professional',
    'Professional Individual Contributor', 'Supervisor',
  ],
  industry: [
    'Banking/Finance', 'Healthcare', 'Hospitality', 'Insurance',
    'Manufacturing', 'Oil & Gas', 'Retail', 'Telecommunications',
  ],
  language: [
    'English (USA)', 'English (UK)', 'English International', 'Spanish',
    'French', 'German', 'Chinese Simplified', 'Japanese', 'Portuguese',
    'Portuguese (Brazil)',
  ],
  job_category: [
    'Architecture and Engineering', 'Arts, Design, and Media',
    'Building and Grounds Cleaning and Maintenance', 'Business and Financial Operations',
    'Community and Social Services', 'Computer and Mathematical', 'Construction and Extraction',
    'Contact Center and Customer Service', 'Education, Training, and Library',
    'Farming, Fishing, and Forestry', 'Food Preparation and Serving Related',
    'Health and Environmental Science', 'Healthcare Practitioners and Technical',
    'Healthcare Support', 'Legal', 'Management and Leadership',
    'Office and Administrative Support', 'Personal Care and Service', 'Production',
    'Protective Service', 'Sales and Related',
    'Skilled Electrical, Mechanical, and Industrial', 'Transportation and Material Moving',
  ],
} as const;
