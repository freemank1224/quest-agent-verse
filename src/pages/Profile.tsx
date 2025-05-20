
import React, { useState } from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import Navbar from '@/components/Navbar';

const Profile = () => {
  const { user, profile, isLoading, signOut, updateProfile } = useAuth();
  
  const [formData, setFormData] = useState({
    username: profile?.username || '',
    first_name: profile?.first_name || '',
    last_name: profile?.last_name || '',
    avatar_url: profile?.avatar_url || '',
  });
  
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin h-8 w-8 border-4 border-primary border-t-transparent rounded-full mx-auto mb-4"></div>
          <p>加载中...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/auth" replace />;
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    
    try {
      await updateProfile(formData);
      setIsEditing(false);
    } catch (error) {
      console.error('Error updating profile:', error);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      
      <div className="container py-12 px-4 max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-8 text-center">个人资料</h1>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <Card className="col-span-1 bg-white shadow-md">
            <CardHeader>
              <CardTitle>个人信息</CardTitle>
              <CardDescription>您的账户详情</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4 text-center">
              <div className="w-24 h-24 mx-auto bg-gray-200 rounded-full overflow-hidden">
                {profile?.avatar_url ? (
                  <img 
                    src={profile.avatar_url} 
                    alt={profile.username || '用户头像'} 
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <div className="flex items-center justify-center h-full bg-primary/10 text-primary font-bold text-2xl">
                    {profile?.username?.charAt(0)?.toUpperCase() || user.email?.charAt(0)?.toUpperCase() || '?'}
                  </div>
                )}
              </div>
              <div>
                <h3 className="font-medium text-lg">{profile?.username || '未设置用户名'}</h3>
                <p className="text-gray-500">{user.email}</p>
              </div>
              <Button 
                variant="outline" 
                className="w-full" 
                onClick={signOut}
              >
                退出登录
              </Button>
            </CardContent>
          </Card>
          
          <Card className="col-span-1 md:col-span-2 bg-white shadow-md">
            <CardHeader>
              <div className="flex justify-between items-center">
                <div>
                  <CardTitle>个人资料</CardTitle>
                  <CardDescription>管理您的个人资料信息</CardDescription>
                </div>
                {!isEditing && (
                  <Button 
                    variant="outline" 
                    onClick={() => setIsEditing(true)}
                  >
                    编辑资料
                  </Button>
                )}
              </div>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit}>
                <div className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="username">用户名</Label>
                      <Input
                        id="username"
                        name="username"
                        value={formData.username || ''}
                        onChange={handleChange}
                        disabled={!isEditing}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="avatar_url">头像链接</Label>
                      <Input
                        id="avatar_url"
                        name="avatar_url"
                        value={formData.avatar_url || ''}
                        onChange={handleChange}
                        disabled={!isEditing}
                        placeholder="https://example.com/avatar.jpg"
                      />
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="first_name">名字</Label>
                      <Input
                        id="first_name"
                        name="first_name"
                        value={formData.first_name || ''}
                        onChange={handleChange}
                        disabled={!isEditing}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="last_name">姓氏</Label>
                      <Input
                        id="last_name"
                        name="last_name"
                        value={formData.last_name || ''}
                        onChange={handleChange}
                        disabled={!isEditing}
                      />
                    </div>
                  </div>
                </div>
                
                {isEditing && (
                  <CardFooter className="px-0 pt-6">
                    <div className="flex gap-2 w-full">
                      <Button 
                        type="button" 
                        variant="outline" 
                        className="flex-1"
                        onClick={() => {
                          setIsEditing(false);
                          setFormData({
                            username: profile?.username || '',
                            first_name: profile?.first_name || '',
                            last_name: profile?.last_name || '',
                            avatar_url: profile?.avatar_url || '',
                          });
                        }}
                      >
                        取消
                      </Button>
                      <Button 
                        type="submit" 
                        className="flex-1"
                        disabled={isSaving}
                      >
                        {isSaving ? '保存中...' : '保存更改'}
                      </Button>
                    </div>
                  </CardFooter>
                )}
              </form>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default Profile;
